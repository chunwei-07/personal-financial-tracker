// Converts an array of objects to CSV-string
function convertToCSV(data) {
    if (!data || data.length === 0) {
        return "";
    }

    // Define the headers in CSV
    const headers = [
        'date', 'type', 'description', 'category',
        'amount', 'from_account', 'to_account'
    ];

    // Function to sanitize and format a cell value
    const formatCell = (value) => {
        if (value === null || value === undefined) {
            return '';
        }
        let cell = String(value);

        // If the cell has comma, double quotes, or new line, wrap in double quotes
        if (cell.search(/("|,|\n)/g) >= 0) {
            // Escape existing double quotes by doubling them
            cell = '"' + cell.replace(/"/g, '""') + '"';
        }
        return cell;
    };

    // Create the header row
    const headerRow = headers.map(h => formatCell(h)).join(',');

    // Create the data rows
    const dataRows = data.map(row => {
        return headers.map(header => {
            return formatCell(row[header]);
        }).join(',');
    });

    // Combine the header and data rows
    return [headerRow, ...dataRows].join('\n');
}

// Triggers a browser download for the given CSV content
export function downloadCSV(csvContent, fileName) {
    // Create a Blob from CSV String
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

    // Create a temporary link element
    const link = document.createElement("a");
    if (link.download !== undefined) {
        // Check if browser supports the download attribute
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", fileName);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);

        // Programatically click the link to trigger download
        link.click();

        // Clean up by removing the link
        document.body.removeChild(link);
        URL.revokeObjectURL(url);   // Free up memory
    }
}

export default convertToCSV;