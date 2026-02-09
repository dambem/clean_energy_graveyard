// mapUtils.js
export async function addMarkerLayer(map) {
    map.addLayer({
        id: 'places',
        type: 'symbol',
        source: 'points',
        layout: {
            'icon-image': 'triangle',
            'icon-size': 2,
            'icon-allow-overlap': true,
            'icon-padding': 2
        },
        'paint': {
            'icon-color': '#8B4513',
            'icon-halo-color': '#FFFFFF',
            'icon-halo-width': 2,
        }
    });
}

export async function addLocalAuthoritiesSource(map, geojsonData) {
    map.addSource('local-authorities',  {
        type: 'geojson',
        data: geojsonData
    });
}

export async function addLocalAuthoritiesLayer(map) {
    map.addLayer({
        'id': 'local-authorities-layer',
        'source': 'local-authorities',
        'type':'fill',
        'paint': {
            'fill-outline-color': 'white',
            'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'hover'], false],
                0.9,
                [
                    'interpolate', ['linear'],
                    ['get', 'project_count'],
                    0, 0.05,
                    1, 0.4,
                    5, 0.6,
                    15, 0.8
                ]
            ],
            'fill-color': [
                'interpolate', ['linear'],
                ['get', 'project_count'],
                0, '#f0f0f0',
                1, '#fdd49e',
                3, '#fdbb84',
                5, '#fc8d59',
                10, '#e34a33',
                15, '#b30000'
            ],
        }
    });
}

export async function addNimbyLayer(map, nimbyRefIds, nimbyRefIds2, nimbyRefIds3) {
    let refProperty = 'Ref ID';
    map.addLayer({ 
        id: 'unclustered-point',
        type: 'circle',
        source: 'points',
        paint: {
            'circle-radius': [
                'interpolate',
                ['linear'],
                ['coalesce', ['get', sizeProperty], 0],
                0, 5,
                200, 20
            ],
            'circle-stroke-width': 0,
            'circle-stroke-opacity':0.5,

            'circle-color': [
                'case',
                ['boolean', ['feature-state', 'selected'], false],
                '#fbb03b',  // Selected color
                [
                    'case',
                    ['in', ['get', refProperty], ['literal', [...nimbyRefIds]]],
                    '#97001b',  // Has nimby details - darker red
                    [
                        'case',
                        ['in', ['get', refProperty], ['literal', [...nimbyRefIds3]]],
                        '#FF446b',  // Has nimby details - darker red
                        [
                            'case',    
                                ['in', ['get', refProperty], ['literal', [...nimbyRefIds2]]],
                                '#a698b8',
                                '#d3d3d3'   // No nimby details - gray
                        ]
                    ]
                ]
            ],
            'circle-opacity': 0
        }
    });

}

export async function addRenewableProjectsSource(map, geojsonData) {
    map.addSource('points', {
        type: 'geojson',
        data: {
            type: 'FeatureCollection',
            features: points
        }
    });
}