from funcs import repd_converter as repd
from funcs import scrape_and_analyse as scrape
import json
import time
import os 
import sys
import pandas as pd
class NimbyParser:
    def __init__(self):
        pass

    
def nimby_parse():
    repd.repd_geojson_file()
    
    df = repd.get_repd_dataframe()
    df = df.sort_values(by=['Installed Capacity (MWelec)'], ascending=False)
    
    nimby_radar = {}
    nimby_scores = []
    score = 0
    start_row = 5
    
    if os.path.exists("nimby_score.json"):
        with open("nimby_score.json", "r", encoding="utf-8") as f:
            try:
                for n in json.load(f):
                    nimby_scores.append(n)
            except json.JSONDecodeError:
                pass
    df_2 = pd.DataFrame(nimby_scores)
    all_set = set(df['Ref ID'])
    json_set = set(df_2['refid'])
    diff = all_set.difference(json_set)
    remaining = df[df['Ref ID'].isin(diff)]
    
    for _, row in remaining.iloc[start_row:].iterrows():
        string = f"{row['Site Name']}, {row['Planning Authority']} "
        query_res = repd.search_query(string)
        if query_res:
            url = query_res[0]["link"] 
            mime = 'n/a'
            if query_res[0].get('mime'):
                mime = query_res[0]['mime']
            
            
            content = scrape.scrape_content(url, mime=mime)
            time.sleep(5)
            if content == None:
                content = "Nothing located - please fill with default 0 values and write a snippy remark"
            ai = scrape.gemini_process(content)
            new_text = ai.replace("json", "")
            new_text = new_text.replace("```", "")
            try:
                object = json.loads(new_text)
                ref_id = row['Ref ID']
                object['refid'] = ref_id
                object['article_url'] = url
                nimby_scores.append(object)    
            except Exception:
                next
            with open("nimby_score.json", "w", encoding="utf-8") as f: 
                json.dump(nimby_scores, f, ensure_ascii=False, indent=4)
            time.sleep(5)
        if score >= 15:
            sys.exit(0)
        else:
            score += 1
            
    


if __name__ == "__main__":    
    scrape.convert_points_geojson()
    # dorset.main()
    # df = repd.get_repd_dataframe()
    # df = df.sort_values(by=['Installed Capacity (MWelec)'], ascending=False)

    # print(df)
    # df.to_csv("test.csv")
    repd.repd_geojson_file()
