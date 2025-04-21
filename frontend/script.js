async function fetchStockData() {
    try {
        console.log("Fetching stock data...");
        const response = await fetch("http://127.0.0.1:5000/api/get_all_stocks");
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

        const data = await response.json();
        updateTable(data);
    } catch (error) {
        console.error("Error fetching stock data:", error);
        document.getElementById("stockData").innerHTML = "<tr><td colspan='9'>Failed to load data. Please refresh.</td></tr>";
    }
}

function updateTable(data) {
    if (!Array.isArray(data) || data.length === 0) {
        console.warn("No data received!");
        document.getElementById("stockData").innerHTML = "<tr><td colspan='9'>No stock data available</td></tr>";
        return;
    }

    let tableHTML = "";
    data.forEach(stock => {
        const price = stock.current_price?.toFixed(2) || "N/A";
        const future_price = stock.future_price?.toFixed(2) || "N/A";
        const daily_change = stock.daily_change_percent !== null ? stock.daily_change_percent.toFixed(2) + "%" : "N/A";
        const rsi = stock.rsi?.toFixed(2) || "N/A";
        const eps_growth = stock.eps_growth?.toFixed(2) || "N/A";
        const trend = stock.trend || "Unknown";
        const buying_price = stock.buying_price?.toFixed(2) || "N/A";

        let recommendationClass = "secondary";
        if (stock.recommendation === "Strong Buy") recommendationClass = "success";
        else if (stock.recommendation === "Buy") recommendationClass = "primary";
        else if (stock.recommendation === "Overbought - Potential Correction") recommendationClass = "warning";
        else if (stock.recommendation === "Sell") recommendationClass = "danger";
        else if (stock.recommendation === "Hold") recommendationClass = "info";

        tableHTML += `<tr>
            <td>${stock.symbol}</td>
            <td>₹${price}</td>
            <td>₹${future_price}</td>
            <td class="${stock.daily_change_percent >= 0 ? 'positive' : 'negative'}">${daily_change}</td>
            <td>${rsi}</td>
            <td>${eps_growth}</td>
            <td>${trend}</td>
            <td>₹${buying_price}</td>
            <td><span class="badge bg-${recommendationClass}">${stock.recommendation || "N/A"}</span></td>
        </tr>`;
    });

    document.getElementById("stockData").innerHTML = tableHTML;
}

document.addEventListener("DOMContentLoaded", fetchStockData);
