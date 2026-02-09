import io
from playwright.async_api import async_playwright, TimeoutError
from pypdf import PdfReader

# --- Configuration ---
BASE_URL = "https://planning.dorsetcouncil.gov.uk/?AspxAutoDetectCookieSupport=1"

async def analyze_application_documents(app_number: str):
    """
    Analyzes documents for a given Dorset Council planning application number.

    Args:
        app_number: The planning application reference (e.g., "P/FUL/2023/02446").
    """
    print(f"🚀 Starting analysis for application: {app_number}")
    
    async with async_playwright() as p:
        # Launch a headless browser (headless=True means it runs in the background)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # 1. Navigate to the main page
            print("➡️ Navigating to the planning portal...")
            await page.goto(BASE_URL, timeout=60000)

            # 2. Handle the cookie banner
            try:
                # Use a robust selector to find the accept button
                await page.get_by_role("button", name="Accept").click(timeout=10000)
                print("✔️ Accepted cookie policy.")
            except TimeoutError:
                print("⚠️ Cookie banner not found, assuming it was already accepted.")

            # 3. Search for the application
            print(f"➡️ Searching for '{app_number}'...")
            search_input = page.get_by_label("Search for a planning application")
            await search_input.fill(app_number)
            await page.get_by_role("button", name="Search").click()
            
            # 4. Navigate to the documents tab
            print("➡️ Navigating to the 'Documents' tab...")
            # Wait for the results to load by looking for the application summary
            await page.wait_for_selector(f"h1:has-text('{app_number}')", timeout=30000)
            await page.get_by_role("link", name="Documents").click()

            # 5. Scrape the document list
            print("🔍 Scraping document list...")
            # Wait for the table to be visible
            await page.wait_for_selector("table#Documents", timeout=30000)
            
            document_rows = await page.locator("table#Documents tbody tr").all()
            
            documents_data = []
            if not document_rows:
                print("❌ No documents found for this application.")
                return

            print(f"✅ Found {len(document_rows)} documents. Analyzing each...")

            for i, row in enumerate(document_rows):
                # Extract basic info directly from the table
                description = await row.locator("td:nth-child(2)").inner_text()
                file_size = await row.locator("td:nth-child(4)").inner_text()
                link_element = row.locator("td:nth-child(2) a")
                
                doc_info = {
                    "description": description.strip(),
                    "file_size": file_size.strip(),
                    "page_count": "N/A",
                    "url": ""
                }

                # Check if a link exists
                if await link_element.count() > 0:
                    href = await link_element.get_attribute("href")
                    # The URL is relative, so we need to construct the full URL
                    full_url = f"https://planning.dorsetcouncil.gov.uk{href}"
                    doc_info["url"] = full_url

                    # 6. Analyze PDF for page count
                    if href.lower().endswith(".pdf"):
                        print(f"   Analysing PDF ({i+1}/{len(document_rows)}): {description[:50]}...")
                        try:
                            # Use the browser's context to download the file,
                            # ensuring we have the correct session/cookies.
                            api_request_context = page.context.request
                            response = await api_request_context.get(full_url)
                            pdf_bytes = await response.body()
                            
                            # Read the PDF from memory
                            pdf_file = io.BytesIO(pdf_bytes)
                            reader = PdfReader(pdf_file)
                            doc_info["page_count"] = len(reader.pages)
                        except Exception as e:
                            print(f"      - Error analyzing PDF: {e}")
                            doc_info["page_count"] = "Error"
                
                documents_data.append(doc_info)

            # 7. Print the final report
            print("\n" + "="*80)
            print(f"📋 Document Analysis Report for: {app_number}")
            print("="*80)
            # Find max length for clean formatting
            max_desc = max(len(d['description']) for d in documents_data) if documents_data else 20
            
            print(f"{'Document Description'.ljust(max_desc)} | {'File Size'.ljust(10)} | {'Page Count'}")
            print(f"{'-'*max_desc} | {'-'*10} | {'-'*10}")

            for doc in documents_data:
                print(f"{doc['description'].ljust(max_desc)} | {doc['file_size'].ljust(10)} | {str(doc['page_count'])}")
            
            print("="*80)

        except TimeoutError as e:
            print("\n❌ A timeout occurred. The page might have changed, or the application number is invalid.")
            print(f"   Details: {e}")
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
        finally:
            await browser.close()
            print("✅ Analysis complete. Browser closed.")


async def main():
    # --- CHANGE THIS TO THE APPLICATION YOU WANT TO ANALYZE ---
    application_to_check = "P/FUL/2023/02446"
    await analyze_application_documents(application_to_check)


# if __name__ == "__main__":
#     asyncio.run(main())