<script>
export async function addMarkerLayer(map) {

    // Add the layer using the marker
    map.addLayer({
        id: 'places',
        type: 'symbol',
        source: 'points',
        layout: {
            'icon-image': 'triangle',
            'icon-size': 2,  // Adjust size as needed
            'icon-allow-overlap': true,
            'icon-padding': 2

        },
        'paint': {
            // If icons are SDF, you can color them
            'icon-color': '#8B4513', // Brown for monuments
            'icon-halo-color': '#FFFFFF',
            'icon-halo-width': 2,
        }
    });
}
</script>
