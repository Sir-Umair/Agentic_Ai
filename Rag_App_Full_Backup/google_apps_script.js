/**
 * Google Apps Script to be deployed as a Web App.
 * 
 * 1. Open Sheets (sheets.new)
 * 2. Extensions > Apps Script
 * 3. Paste this code
 * 4. Deploy > New Deployment > Web App
 * 5. Execute as: Me
 * 6. Who has access: Anyone
 */

function doPost(e) {
    try {
        var data = JSON.parse(e.postData.contents);
        var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

        // Add header if sheet is empty
        if (sheet.getLastRow() == 0) {
            sheet.appendRow(["Student Name", "Roll No", "Pages", "Marks", "Timestamp"]);
        }

        sheet.appendRow([
            data.name,
            data.roll_number,
            data.page_count,
            data.marks,
            new Date()
        ]);


        return ContentService.createTextOutput(JSON.stringify({ "status": "success" }))
            .setMimeType(ContentService.MimeType.JSON);

    } catch (error) {
        return ContentService.createTextOutput(JSON.stringify({ "status": "error", "message": error.toString() }))
            .setMimeType(ContentService.MimeType.JSON);
    }
}
