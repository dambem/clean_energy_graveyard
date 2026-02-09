export async function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        console.log('Async: Copying to clipboard was successful!');
        return "Copied!";
    } catch (err) {
        console.error('Async: Could not copy text: ', err);
    });



}