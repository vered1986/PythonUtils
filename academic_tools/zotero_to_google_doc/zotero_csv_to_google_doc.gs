/**
 * Generate Google Doc from Zotero CSV
 * Before running the script, make sure you have a single file named zotero_input.
 * Author: Vered Shwartz, 2020. 
 *
 * Based on script from Mikko Ohtamaa, http://opensourcehacker.com
 */

/**
 * Return spreadsheet row content as JS array.
 */
function getRowAsArray(dataRange, row, num_columns) {
  var columns = [];

  for (var j = 1; j <= num_columns; j++) {
    var col = dataRange.getCell(row,j).getValue();
    columns.push(col);
  }

  return columns;
}

/**
 * Get HTML string and paste it as formatted text in the doc. 
 */
function render_html(html) {
  html = html.replace("<h2>Summary</h2> ", ""); 
  var blob = DriveApp.createFile('temp_zotero', html, 'text/html').getBlob();
  var resource = {
    title: 'temp_zotero',
    convert: true,
    mimeType: 'application/vnd.google-apps.document' 
  };
  var newFile = Drive.Files.insert(resource, blob);
  var doc = DocumentApp.openById(newFile.getId());
  var body = doc.getBody().copy();
  DriveApp.removeFile(DriveApp.getFileById(doc.getId()));  
  mergeDocs(body);
}

/**
 * Copy content of one Google Doc into another. 
 */
function mergeDocs(otherBody) {
  var body = DocumentApp.getActiveDocument().getBody();
  var totalElements = otherBody.getNumChildren();
  var list_ids = [];
  
  for(var j = 0; j < totalElements; ++j) {
    var element = otherBody.getChild(j).copy();
    var type = element.getType();
    
    // Paragraph
    if(type == DocumentApp.ElementType.PARAGRAPH) {
      body.appendParagraph(element);
      body.appendParagraph("");
    }
    // List item
    else if(type == DocumentApp.ElementType.LIST_ITEM) {
      
      var list_item = element.copy().asListItem();
      
      // First list item - restart numbering
      if ((j == 0) || (otherBody.getChild(j-1).getType() != DocumentApp.ElementType.LIST_ITEM)){
        list_ids.push( body.appendListItem("temp"));
      }
      
      var list_id = list_ids[list_ids.length - 1];
      
      // appendListItem() resets glyph type
      glyphType = list_item.getGlyphType();
      body.appendListItem(list_item);
      list_item.setGlyphType(glyphType);
      list_item.setListId(list_id);
      
      // Space after the list
      if ((j == totalElements - 1) || (otherBody.getChild(j+1).getType() != DocumentApp.ElementType.LIST_ITEM)){
        body.appendParagraph("");
      }
    }
  }
  
  list_ids.forEach(function (list_id) {
    body.removeChild(list_id);  
  });
}

/**
 * Add a single paper to the document. 
 */
function add_paper(rangeData, index, body, num_columns){
  var paper_data = getRowAsArray(rangeData, index, num_columns);  
  Logger.log("Processing data:" + paper_data);

  // Get fields
  var title = paper_data[4].replace(/\s\s+/g, ' ');
  var authors = paper_data[3];
  var year = paper_data[2];
  var venue = paper_data[5].replace(/\s\s+/g, ' ');
  var url = paper_data[9];
  var notes = paper_data[36]; 
  
  var par1 = body.appendParagraph(title);
  par1.setHeading(DocumentApp.ParagraphHeading.HEADING4);
  
  // Convert the authors to First Name Last Name
  var authors_list = authors.split("; ");
  var authors_list_new = [];
  authors_list.forEach(function (author) {
    var names = author.split(", ");
    authors_list_new.push(names[1] + " " + names[0]);
  });
  authors = authors_list_new.join(", ");
  Logger.log("Processing columns:" + authors);
  var par2 = body.appendParagraph(authors);
  par2.setHeading(DocumentApp.ParagraphHeading.NORMAL);
  
  var par3 = body.appendParagraph(venue + ". " + year);
  par3.setHeading(DocumentApp.ParagraphHeading.NORMAL);
  par3.setItalic(true);
  
  var par4 = body.appendParagraph("[Paper]");
  par4.setHeading(DocumentApp.ParagraphHeading.NORMAL);
  par4.setLinkUrl(url);
  
  // Add the notes
  body.appendParagraph("");
  render_html(notes);
}


function main() {
  // Open the input file
  var files = DriveApp.searchFiles('title contains "zotero_input"');
  while (files.hasNext()) {
    var spreadsheet = SpreadsheetApp.open(files.next());
    var data = spreadsheet.getSheets()[0];
  }
  
  var body = DocumentApp.getActiveDocument().getBody();
  
  // Heading
  var par = body.appendParagraph("Imported Papers");
  par.setHeading(DocumentApp.ParagraphHeading.HEADING3);
  
  // Iterate over papers (first row is header)
  var rangeData = data.getDataRange();
  var num_rows = rangeData.getLastRow();
  var num_columns = rangeData.getLastColumn();

  for (index = 2; index < num_rows + 1; index++){
    add_paper(rangeData, index, body, num_columns);
  };
}