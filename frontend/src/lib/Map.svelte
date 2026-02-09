<script>
    import { onMount, onDestroy } from "svelte";
    import maplibregl from "maplibre-gl";
    import "maplibre-gl/dist/maplibre-gl.css";
    import Chart from "chart.js/auto";
    import { cubicIn, cubicOut } from "svelte/easing";
    import { slide } from "svelte/transition";
    import gsap from "gsap";
    import DelayTimesVisualization from "$lib/components/DelayTimesVisualization.svelte";
    import Cards from "$lib/components/Cards.svelte";
    import { PUBLIC_MAPTILER_API_KEY } from "$env/static/public";
    import Timeline from "$lib/components/Timeline.svelte";
    import { fly } from "svelte/transition";
    import About from "$lib/components/About.svelte";
    import Badge from "./components/ui/badge/badge.svelte";
    import marker from "/src/icons/marker.svg";
    import SelectedFeatureUI from "./components/sidebar/SelectedFeatureUI.svelte";
    import SideBarMain from "./components/sidebar/SideBarMain.svelte";
    import {
        addMarkerLayer,
        addLocalAuthoritiesSource,
        addNimbyLayer,
        addLocalAuthoritiesLayer,
        addRenewableProjectsSource,
    } from "$lib/utils/mapUtils.js";
    let isCollapsed = false;
    let config;

    export let points = []; // GeoJSON features
    export let nimby_score = [];
    export let councils = [];
    export let refused = [];
    export let sizeProperty = "Installed Capacity (MWelec)";
    export let typeProperty = "Technology Type";
    export let refProperty = "Ref ID";

    export let minSize = 20;
    export let maxSize = 50;
    let coloringMode = "nimby"; // Start with NIMBY coloring, options are 'nimby' or 'type'
    let showControlPanel = false;
    let filterSolar = true;
    let filterWind = true;
    let filterBattery = true;
    let filterOther = true;
    let showLocalAuthorities = true;
    let showProjects = true;
    // DOM elements
    const NIMBY_TEST = "#b62121";
    const NIMBY_POTENTIAL = "#eb8e47";
    let mapContainer;
    let nimbyRadarCanvas;
    let sidebarContent;
    let typeItems2 = [
        { label: "Battery", color: "#004C99" },
        { label: "Solar", color: "#E6B800" },
        { label: "Wind", color: "#00857D" },
        { label: "Other", color: "#FFFFFF" },
    ];

    let typeItems = [
        { label: "Not A NIMBY", color: "#d3d3d3" },
        { label: "Nimby Potential", color: NIMBY_POTENTIAL },
        { label: "NIMBY", color: NIMBY_TEST },
    ];
    let currentTypeLabel = typeItems;

    // State variables
    let map;
    let selectedFeature = null;
    let nimby_choice = null;
    let speed = 0;
    let rpm = 0;
    let radarChart = null;
    let showSubmitForm = false;
    let articleUrl = "";
    let articleNotes = "";

    // Date filter
    let startDate = "2020-01-01";
    let endDate = "2025-01-01";
    let technologyType = "all";
    const accuracy2 = nimby_score.filter(
        (item) => item["Accuracy Score"] >= 30,
    );
    const accuracy3 = nimby_score.filter(
        (item) => item["Accuracy Score"] < 70 && item["Accuracy Score"] >= 50,
    );
    const accuracy1 = nimby_score.filter(
        (item) => item["Accuracy Score"] >= 70,
    );
    const accuracy_bad = nimby_score.filter(
        (item) => item["Accuracy Score"] < 30,
    );
    const nimbyRefIds = new Set(accuracy1.map((item) => item.refid || ""));
    const nimbyRefIds2 = new Set(accuracy_bad.map((item) => item.refid || ""));
    const nimbyRefIds3 = new Set(accuracy2.map((item) => item.refid || ""));
    const nimbyRefIds4 = new Set(accuracy3.map((item) => item.refid || ""));
    let stats = [
        {
            label: "Total Capacity Lost",
            value: "6584",
            calculate: calculateTotalCapacity,
            trend: "MW",
        },
        {
            label: "Total Projects Cancelled",
            value: "156",
            calculate: calculateLengthA,
            trend: "Since January 2020",
        },
    ];

    const allowedProperties = [
        "Operator (or Applicant)",
        "Site Name",
        "Technology Type",
        "Installed Capacity (MWelec)",
        "Development Status",
        "Planning Permission Refused",
        "Planning Application Withdrawn",
        "Planning Application Submitted",
    ];

    // Animation timer
    let animationTimer;
    function updateCircleColors() {
        if (!map || !map.getLayer("unclustered-point")) return;
        if (coloringMode === "nimby") {
            // NIMBY-based coloring
            map.setPaintProperty(
                "unclustered-point",
                "circle-color",
                "#ffffff",
            ); // Base color

            map.setPaintProperty("unclustered-point", "circle-color", [
                "case",
                ["in", ["get", refProperty], ["literal", [...nimbyRefIds]]],
                NIMBY_TEST, // Has nimby details - darker red
                [
                    "case",
                    [
                        "in",
                        ["get", refProperty],
                        ["literal", [...nimbyRefIds3]],
                    ],
                    NIMBY_POTENTIAL, // Has nimby details - darker red
                    [
                        "case",
                        [
                            "in",
                            ["get", refProperty],
                            ["literal", [...nimbyRefIds2]],
                        ],
                        NIMBY_POTENTIAL,
                        "#d3d3d3", // No nimby details - gray
                    ],
                ],
            ]);
            // Reset stroke to a simple style
            map.setPaintProperty(
                "unclustered-point",
                "circle-stroke-color",
                "#000000",
            );
            map.setPaintProperty(
                "unclustered-point",
                "circle-stroke-width",
                0.5,
            );
        } else {
            // Type-based coloring
            map.setPaintProperty(
                "unclustered-point",
                "circle-color",
                "#ffffff",
            ); // Base color
            // Use the type colors for the stroke
            map.setPaintProperty("unclustered-point", "circle-color", [
                "match",
                ["get", typeProperty], // Get the value of typeProperty
                "Battery",
                "#004C99", // Blue for battery
                "Solar Photovoltaics",
                "#E6B800", // Gold for solar
                "Wind Onshore",
                "#00CC66", // Green for wind
                "#FFFFFF", // Default color if none match
            ]);
            map.setPaintProperty("unclustered-point", "circle-stroke-width", 2);
        }
    }
    function toggleColorMode() {
        coloringMode = coloringMode === "nimby" ? "type" : "nimby";
        currentTypeLabel = coloringMode === "nimby" ? typeItems : typeItems2;
        updateCircleColors();
    }

    function toggleLayerVisibility(layerId, visible) {
        if (!map || !map.getLayer(layerId)) return;
        map.setLayoutProperty(layerId, "visibility", visible ? "visible" : "none");
    }

    function enrichAuthoritiesWithProjectCounts(authoritiesData, projectFeatures) {
        const projectCounts = {};
        const capacityCounts = {};
        projectFeatures.forEach((feature) => {
            const authority =
                feature.properties["Planning Authority"] || "Unknown";
            projectCounts[authority] = (projectCounts[authority] || 0) + 1;
            capacityCounts[authority] =
                (capacityCounts[authority] || 0) +
                (parseFloat(
                    feature.properties["Installed Capacity (MWelec)"],
                ) || 0);
        });

        authoritiesData.features.forEach((feature) => {
            const name = feature.properties.LAD24NM;
            feature.properties.project_count = projectCounts[name] || 0;
            feature.properties.total_capacity = Math.round(
                capacityCounts[name] || 0,
            );
        });
    }
    function calculateTotalCapacity(points) {
        const total = points.reduce((sum, point) => {
            const capacity =
                parseFloat(point.properties["Installed Capacity (MWelec)"]) ||
                0;
            return sum + capacity;
        }, 0);
        return `${Math.round(total)}`;
    }
    function calculateLength(points) {
        // Count points with appeal information
        const appealsCount = points.filter(
            (point) =>
                point.properties["Development Status"] ===
                "Planning Permission Refused",
        ).length;
        return appealsCount.toString();
    }
    function calculateLengthW(points) {
        // Count points with appeal information
        const appealsCount = points.filter(
            (point) =>
                point.properties["Development Status"] ===
                "Planning Application Withdrawn",
        ).length;
        return appealsCount.toString();
    }
    function calculateLengthA(points) {
        // Count points with appeal information
        const appealsCount = points.length;
        return appealsCount.toString();
    }

    function initAnimation() {
        clearInterval(animationTimer);
        animationTimer = setInterval(() => {
            const timeFraction = (Date.now() % 6000) / 5000;
            speed = cubicIn(timeFraction) * 100;
            rpm = cubicOut(timeFraction) * 8000;
        }, 500);
    }

    function getActiveTypes() {
        const types = [];
        if (filterSolar) types.push("Solar Photovoltaics");
        if (filterWind) types.push("Wind Onshore");
        if (filterBattery) types.push("Battery");
        if (filterOther) types.push("Other");
        return types;
    }

    function updateMapData() {
        if (!map) return;
        const activeTypes = getActiveTypes();
        var filter = [
            "all",
            [">=", ["get", "Planning Application Submitted"], startDate],
            ["<=", ["get", "Planning Application Submitted"], endDate],
        ];
        if (activeTypes.length < 4) {
            // Build a match expression: true if type is in activeTypes, also allow through types
            // that don't match any known category when "Other" is on
            filter.push([
                "any",
                ["in", ["get", "Technology Type"], ["literal", activeTypes]],
                ...(filterOther
                    ? [
                          [
                              "all",
                              ["!=", ["get", "Technology Type"], "Solar Photovoltaics"],
                              ["!=", ["get", "Technology Type"], "Wind Onshore"],
                              ["!=", ["get", "Technology Type"], "Battery"],
                          ],
                      ]
                    : []),
            ]);
        }
        map.setFilter("unclustered-point", filter);

        stats.forEach((stat) => {
            const currentValue = stat.calculate(points);
            stat.value = currentValue;
        });
        stats = stats.map((stat) => ({ ...stat }));
    }

    function initMap() {
        if (map) return;

        map = new maplibregl.Map({
            container: mapContainer,
            style: `https://api.maptiler.com/maps/landscape/style.json?key=${PUBLIC_MAPTILER_API_KEY}`,
            center: [-4, 55.2],
            zoom: 4.8,
        });

        map.on("load", () => {
            // Enrich local authorities with project counts before adding source
            enrichAuthoritiesWithProjectCounts(config, points);

            // Add source
            addLocalAuthoritiesSource(map, config);
            map.addSource("points", {
                type: "geojson",
                data: {
                    type: "FeatureCollection",
                    features: points,
                },
            });
            addLocalAuthoritiesLayer(map);

            const popup = new maplibregl.Popup({
                closeButton: false,
                closeOnClick: false,
            });
            let hoveredPointId = null;
            let hoveredAuthorityId = null;

            // Add circle layer for project markers
            map.addLayer({
                id: "unclustered-point",
                type: "circle",
                source: "points",
                paint: {
                    "circle-radius": [
                        "interpolate",
                        ["linear"],
                        ["coalesce", ["get", sizeProperty], 0],
                        0, 6,
                        50, 14,
                        200, 22,
                    ],
                    "circle-color": [
                        "case",
                        ["boolean", ["feature-state", "selected"], false],
                        "#fbb03b",
                        [
                            "case",
                            ["in", ["get", refProperty], ["literal", [...nimbyRefIds]]],
                            NIMBY_TEST,
                            [
                                "case",
                                ["in", ["get", refProperty], ["literal", [...nimbyRefIds3]]],
                                NIMBY_POTENTIAL,
                                [
                                    "case",
                                    ["in", ["get", refProperty], ["literal", [...nimbyRefIds2]]],
                                    NIMBY_POTENTIAL,
                                    "#d3d3d3",
                                ],
                            ],
                        ],
                    ],
                    "circle-stroke-color": "#000000",
                    "circle-stroke-width": 0.5,
                    "circle-opacity": 0,
                },
            });

            // Fade in the circles
            setTimeout(() => {
                map.setPaintProperty(
                    "unclustered-point",
                    "circle-opacity-transition",
                    { duration: 800, delay: 100 },
                );
                map.setPaintProperty(
                    "unclustered-point",
                    "circle-opacity",
                    0.85,
                );
            }, 300);
            // Add interactivity
            map.on("mousemove", (e) => {
                // Use queryRenderedFeatures to check for features at the mouse position
                // The first argument is the point, and the second is an object specifying the layers to query.
                const queryLayers = ["local-authorities-layer"];
                if (map.getLayer("unclustered-point")) queryLayers.unshift("unclustered-point");
                const features = map.queryRenderedFeatures(e.point, {
                    layers: queryLayers,
                });
                // Reset cursor
                map.getCanvas().style.cursor = "";
                popup.remove();

                // Reset previous hover states
                if (hoveredPointId !== null) {
                    map.setFeatureState(
                        { source: "points", id: hoveredPointId },
                        { hover: false },
                    );
                    hoveredPointId = null;
                }
                if (hoveredAuthorityId !== null) {
                    map.setFeatureState(
                        { source: "local-authorities", id: hoveredAuthorityId },
                        { hover: false },
                    );
                    hoveredAuthorityId = null;
                }

                if (features.length > 0) {
                    map.getCanvas().style.cursor = "pointer";

                    // Prioritize the point feature if it's present
                    const pointFeature = features.find(
                        (f) => f.layer.id === "unclustered-point",
                    );

                    if (pointFeature) {
                        hoveredPointId = pointFeature.id;
                        map.setFeatureState(
                            { source: "points", id: hoveredPointId },
                            { hover: true },
                        );
                        popup
                            .setLngLat(e.lngLat)
                            .setHTML(
                                `<h3>${pointFeature.properties["Planning Application Reference"]}</h3><p><b>Name:</b>${pointFeature.properties["Site Name"]}</p><p><b>Planning Authority:</b>${pointFeature.properties["Planning Authority"]}</p>`,
                            )
                            .addTo(map);
                    } else {
                        // If no point, check for an authority feature
                        const authorityFeature = features.find(
                            (f) => f.layer.id === "local-authorities-layer",
                        );
                        if (authorityFeature) {
                            hoveredAuthorityId = authorityFeature.id;
                            map.setFeatureState(
                                {
                                    source: "local-authorities",
                                    id: hoveredAuthorityId,
                                },
                                { hover: true },
                            );
                            const count = authorityFeature.properties.project_count || 0;
                            const capacity = authorityFeature.properties.total_capacity || 0;
                            popup
                                .setLngLat(e.lngLat)
                                .setHTML(
                                    `<h3>${authorityFeature.properties.LAD24NM}</h3>` +
                                    (count > 0
                                        ? `<p><b>Projects:</b> ${count}</p><p><b>Total Capacity:</b> ${capacity} MW</p>`
                                        : ``),
                                )
                                .addTo(map);
                        }
                    }
                }
            });

            // Consolidated mouseleave event
            map.on("mouseleave", "unclustered-point", () => {
                if (hoveredPointId !== null) {
                    map.setFeatureState(
                        { source: "points", id: hoveredPointId },
                        { hover: false },
                    );
                }
                hoveredPointId = null;
                map.getCanvas().style.cursor = "";
                popup.remove();
            });

            map.on("mouseleave", "local-authorities-layer", () => {
                if (hoveredAuthorityId !== null) {
                    map.setFeatureState(
                        { source: "local-authorities", id: hoveredAuthorityId },
                        { hover: false },
                    );
                }
                hoveredAuthorityId = null;
                map.getCanvas().style.cursor = "";
                popup.remove();
            });

            // Handle click events
            map.on("click", "unclustered-point", (e) => {
                if (!e.features.length) return;

                // Clear previous selection
                if (selectedFeature) {
                    map.setFeatureState(
                        {
                            source: "points",
                            id: selectedFeature.properties["Ref ID"],
                        },
                        { selected: false },
                    );
                }

                const feature = e.features[0];
                selectedFeature = feature;

                // Find corresponding nimby score by refid
                const featureId = feature.properties["Ref ID"];
                nimby_choice = nimby_score.find(
                    (score) => score.refid === featureId,
                );

                // Set new selection state
                map.setFeatureState(
                    {
                        source: "points",
                        id: selectedFeature.properties["Ref ID"],
                    },
                    { selected: true },
                );

                // Initialize nimby radar chart if nimby_choice exists
                if (nimby_choice) {
                    setTimeout(() => {
                        animateProperties();
                    }, 10);
                } else {
                    // Show UI for submitting a new article
                    nimby_choice = {
                        header: "No community information available yet",
                        "Interesting Tidbits": [
                            "No information has been added for this project yet.",
                        ],
                        "Snide Commentary":
                            "Help us build our database by submitting information about this project!",
                    };
                }
            });

            // Click on local authority to zoom to its bounds
            map.on("click", "local-authorities-layer", (e) => {
                if (!e.features.length) return;
                const feature = e.features[0];
                const coords = feature.geometry.coordinates;
                const bounds = new maplibregl.LngLatBounds();

                if (feature.geometry.type === "Polygon") {
                    coords[0].forEach((coord) => bounds.extend(coord));
                } else if (feature.geometry.type === "MultiPolygon") {
                    coords.forEach((polygon) =>
                        polygon[0].forEach((coord) => bounds.extend(coord)),
                    );
                }

                map.fitBounds(bounds, { padding: 40, maxZoom: 12 });
            });

            // Initialize map data filter
            updateMapData();
        });
    }

    function animateProperties() {
        if (!sidebarContent) return;

        // Get all property rows
        const rows = sidebarContent.querySelectorAll(".property-row");

        // Reset any existing animations
        gsap.set(rows, { opacity: 0, y: 20 });

        // Create stagger animation for the rows
        gsap.to(rows, {
            duration: 0.5,
            opacity: 1,
            y: 0,
            stagger: 0.1,
            ease: "power2.out",
        });
    }
    function toggleControlPanel() {
        showControlPanel = !showControlPanel;
    }
    function resetSelection() {
        if (selectedFeature && map) {
            map.setFeatureState(
                { source: "points", id: selectedFeature.id },
                { selected: false },
            );
            selectedFeature = null;
            nimby_choice = null;
            showSubmitForm = false;
            articleUrl = "";
            articleNotes = "";
        }
    }

    function handleSubmitArticle() {
        // This function would handle the submission - in a real app, you'd send this to your backend
        console.log("Article submitted:", {
            refid: selectedFeature?.properties?.id || selectedFeature?.id,
            siteName: selectedFeature?.properties["Site Name"],
            articleUrl,
            articleNotes,
        });

        // Show success message and reset form
        alert("Thank you for your submission! We will review it shortly.");
        showSubmitForm = false;
        articleUrl = "";
        articleNotes = "";
    }
    let buttonText = "Copy Ref";

    const copyToClipboard = () => {
        let copy = selectedFeature.properties["Planning Application Reference"];
        navigator.clipboard.writeText(copy).then(() => {
            buttonText = "Copied!";
            setTimeout(() => {
                buttonText = "Copy Ref";
            }, 2000); // Revert the button text after 2 seconds
        });
    };
    // Lifecycle hooks
    onMount(async () => {
        console.log(councils);
        let response = await fetch("/localauth.json");
        config = await response.json();

        gsap.from(mapContainer, {
            opacity: 0,
            duration: 2, // Animation duration in seconds
            ease: "power2.out", // Easing function
            delay: 0.5, // Optional: if you want to delay the animation
        });
        initMap();
        initAnimation();
    });

    onDestroy(() => {
        // Clean up resources
        if (map) map.remove();
        if (radarChart) radarChart.destroy();
        clearInterval(animationTimer);
    });

    // Reactive statements
    $: if (selectedFeature) {
        setTimeout(animateProperties, 0);
    }

    $: if (startDate || endDate || technologyType || filterSolar || filterWind || filterBattery || filterOther) {
        updateMapData();
    }
</script>

<div class="font-sans scrollbar">

    {#if !isCollapsed}
        <div
            class="glass3d-wrapper glass3d p-0 sidebar p-3 overflow-y-scroll scrollbar"
            transition:fly={{ x: -200, duration: 300 }}
        >
            <div class="sidebar-header justify-center items-center">
                <div class=" mb-2">
                    {#if selectedFeature}
                        <SelectedFeatureUI
                            {nimbyRadarCanvas}
                            {councils}
                            {resetSelection}
                            {selectedFeature}
                            {nimby_choice}
                        />
                    {:else}
                        <SideBarMain stat={stats} {refused} />
                    {/if}
                </div>
            </div>
            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-white p-6 rounded-xl shadow-xl border border-gray-100">
            <div class="flex  items-center button">

                <a class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white font-medium rounded-md shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 text-sm" , href="https://form.jotform.com/251386339530055"
                    >
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                    Let's Talk!</a
                >
            </div>

            <div class="flex align-right items-center">
                <a
                    class="inline-flex items-center gap-2 px-4 py-2 bg-green-700 text-white font-medium rounded-md shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 text-sm"
                    href="https://www.gov.uk/government/publications/renewable-energy-planning-database-monthly-extract"
                >
                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path>
                    </svg>
                    V1.0.5 - REPD January 2025</a
                >
            </div>
            </div>
        </div>
    {/if}

    <div class="map-container" bind:this={mapContainer}></div>
    <Timeline
        bind:startDate
        bind:endDate
        minDate="2019-01-01"
        ,
        maxDate="2025-01-01"
        on:change{updateMapData}
    ></Timeline>
    <div
        class="glass3d-wrapper control-content expanded absolute top-2 right-2 transform bg-base-100 p-2 rounded-lg shadow-lg"
    >
        <div>
            <div>
                <button
                    class="p-2 text-xs btn bg-orange-400 text-white rounded-xl"
                    on:click={toggleColorMode}
                >
                    {coloringMode === "nimby"
                        ? "NIMBY Level"
                        : "Renewable Type"}
                </button>
            </div>
            <br />

            <div class="legend-items">
                {#each currentTypeLabel as item}
                    <div class="legend-item">
                        <div
                            class="color-swatch"
                            style="background-color: {item.color}"
                        ></div>
                        <div class="label p-0">{item.label}</div>
                    </div>
                {/each}
            </div>
        </div>

        <hr class="my-2 border-gray-300/40" />

        <div class="text-xs font-semibold mb-1 opacity-70">Filter by Type</div>
        <div class="filter-items">
            <label class="filter-item">
                <input type="checkbox" bind:checked={filterSolar} />
                <span class="filter-swatch" style="background-color: #E6B800"></span>
                Solar
            </label>
            <label class="filter-item">
                <input type="checkbox" bind:checked={filterWind} />
                <span class="filter-swatch" style="background-color: #00CC66"></span>
                Wind
            </label>
            <label class="filter-item">
                <input type="checkbox" bind:checked={filterBattery} />
                <span class="filter-swatch" style="background-color: #004C99"></span>
                Battery
            </label>
            <label class="filter-item">
                <input type="checkbox" bind:checked={filterOther} />
                <span class="filter-swatch" style="background-color: #FFFFFF"></span>
                Other
            </label>
        </div>

        <hr class="my-2 border-gray-300/40" />

        <div class="text-xs font-semibold mb-1 opacity-70">Layers</div>
        <div class="filter-items">
            <label class="layer-toggle">
                <input type="checkbox" bind:checked={showLocalAuthorities}
                    on:change={() => toggleLayerVisibility("local-authorities-layer", showLocalAuthorities)} />

                Local Authorities
            </label>
            <label class="layer-toggle">
                <input type="checkbox" bind:checked={showProjects}
                    on:change={() => toggleLayerVisibility("unclustered-point", showProjects)} />
                Projects
            </label>
        </div>
    </div>
</div>

<style>
    .hidden {
        display: none;
    }
    .stat-detail-r {
        background: -webkit-radial-gradient(#b62121, #eb8e47);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        -webkit-text-stroke: 1px red;
    }
    .stat-detail-l {
        background: -webkit-radial-gradient(#eb8e47, #b62121);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    h1 {
        background: -webkit-radial-gradient(#b62121, #eb8e47);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .control-content {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        max-width: 320px;
        overflow: hidden;
    }

    .control-content.collapsed {
        width: 48px;
        height: 48px;
    }

    .control-content.expanded {
        width: 200px;
    }
    .control-toggle {
        position: absolute;
        top: 12px;
        right: 12px;
        width: 24px;
        height: 24px;
        border: none;
        background: transparent;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 6px;
        transition: background-color 0.2s;
    }

    .control-toggle:hover {
        background: rgba(0, 0, 0, 0.1);
    }
    .sidebar {
        position: absolute;
        left: 0.5vw;
        top: 0.5vw;
        height: calc(100% - 1vw);
        background: rgba(90, 90, 90, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        color: var(--navbar-light-primary);
        font-family: Verdana, Geneva, Tahoma, sans-serif;
        overflow-y: auto;
        width: 33%;
        max-width: 500px;
        z-index: 50;
        overflow-x: hidden;
        padding-right: 5px;
    }

    .toggle-sidebar-btn {
        position: absolute;
        top: 1rem;
        left: 1vw;
        z-index: 100;
        background: rgba(45, 45, 45, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        color: white;

        width: 30px;
        height: 30px;
        cursor: pointer;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.5rem;
    }
    .toggle-sidebar-btn:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: scale(1.05);
    }
    /* Mobile Landscape */
    @media (max-width: 768px) and (orientation: landscape) {
        .sidebar {
            width: 50%; /* Adjust as needed */
            max-width: 280px;
        }
    }

    /* Mobile Portrait */
    @media (max-width: 480px) {
        .sidebar {
            width: 80%;
            max-width: none;
            height: 100%;
            top: 0;
            left: 0;
            border-radius: 0;
        }
    }

    .chat {
        padding-left: 0.5rem;
    }
    .container {
        height: 100vh;
    }
    .color-swatch {
        width: 16px;
        height: 16px;
        border-radius: 4px;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }

    .legend-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .filter-items {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .filter-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.75rem;
        cursor: pointer;
    }
    .filter-item input[type="checkbox"] {
        width: 14px;
        height: 14px;
        cursor: pointer;
        accent-color: #f97316;
    }
    .filter-swatch {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 3px;
        border: 1px solid rgba(0, 0, 0, 0.15);
    }
    .map-container {
        height: 100vh;
    }

    .chat-bubble {
        max-width: 90%;
    }

    .property-row {
        opacity: 0;
    }
</style>
