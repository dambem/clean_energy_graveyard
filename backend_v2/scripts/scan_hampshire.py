from src.processors.repd_processor import REPDProcessor

def main():
    print(f'== Scanning Hampshire ==')
    processor = REPDProcessor()
    date_str = "2025-01-01"
    df = processor.process_pipeline(date=date_str)
    df = processor.filter_by_cancelled(df=df)
    df = df[df['County'] == 'Hampshire']
    df.to_csv(f'outputs/hampshire-{date_str}.csv')
    print(df)

if __name__ == '__main__':
    main()