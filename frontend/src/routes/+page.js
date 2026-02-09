export async function load({ fetch }) {
    try {
      const response = await fetch('/points.geojson');  // Place your GeoJSON in the static folder
      const nimby_r = await fetch('/nimby_score.json');  // Place your GeoJSON in the static folder
      const date_refused = await fetch('/df_refused.json');  // Place your GeoJSON in the static folder
      const date_a_refused = await fetch('/df_withdrawn.json');  // Place your GeoJSON in the static folder
      const date_withdrawn = await fetch('/df_a_refused.json');  // Place your GeoJSON in the static folder
      const final_stats = await fetch('/final.json');  // Place your GeoJSON in the static folder
      const councils = await fetch('/councils.json');  // Place your GeoJSON in the static folder


      const geojson = await response.json();
      const nimby_score = await nimby_r.json();
      const refused = await date_refused.json();
      const a_refused = await date_a_refused.json();
      const withdrawn = await date_withdrawn.json();
      const final_stat = await final_stats.json();
      const council = await councils.json();

      return {
        points: geojson.features,
        nimby_score: nimby_score,
        refused: refused,
        a_refused: a_refused,
        withdrawn: withdrawn,
        final_stats: final_stat,
        council: council
      };
    } catch (error) {
      console.error('Error loading GeoJSON:', error);
      return {
        points: []
      };
    }
  }