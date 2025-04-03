// 🔁 Portfolio data
let portfolio = {};
let gainersOffset = 0;
let chart;
let currentPrice = 100;

// 📈 Load Top Gainers
let allGainers = [];
async function loadGainers() {
  const res = await fetch(`/top-gainers?offset=${gainersOffset}&limit=5`);
  const data = await res.json();
  const tbody = document.querySelector("#gainersTable tbody");
  data.forEach(g => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${g._id}</td><td>${g.price}</td><td>${g.change}</td>`;
    row.onclick = () => autofillAI({ _id: g._id, price: g.price });
    tbody.appendChild(row);
  });
  allGainers = [...allGainers, ...data];
  gainersOffset += 5;
}
document.getElementById("loadMoreGainers").addEventListener("click", loadGainers);
loadGainers();

// 🔍 Autocomplete search
document.getElementById("searchInput").addEventListener("input", async function () {
  const query = this.value.trim();
  const suggestionsBox = document.getElementById("suggestions");
  suggestionsBox.innerHTML = "";
  if (query.length < 2) return;

  const res = await fetch("/autocomplete-symbols", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  const data = await res.json();

  if (data.status === "success") {
    data.matches.forEach(stock => {
      const escapedId = CSS.escape(stock._id);
      const li = document.createElement("li");
      li.className = "list-group-item d-flex justify-content-between align-items-center";
      li.innerHTML = `
        <span><strong>${stock._id}</strong> – ${stock.name}</span>
        <div class="input-group input-group-sm" style="width: 160px;">
          <input type="number" min="1" value="1" class="form-control" id="qty-${escapedId}" style="max-width: 60px;">
          <button class="btn btn-sm btn-outline-primary" onclick="buyStock('${stock._id}'); event.stopPropagation();">Buy</button>
        </div>`;
      li.onclick = () => {
        autofillAI(stock);
        suggestionsBox.innerHTML = "";
      };
      suggestionsBox.appendChild(li);
    });
  }
});

// 🛒 Buy
function buyStock(symbol) {
  const input = document.querySelector(`input[id='qty-${CSS.escape(symbol)}']`);
  if (!input) return alert("Invalid quantity");
  const quantity = parseInt(input.value);
  if (!quantity || quantity <= 0) return alert("Invalid quantity");

  portfolio[symbol] = (portfolio[symbol] || 0) + quantity;
  input.value = "1";
  updatePortfolioUI();
}

// ➖ Sell
function sellStock(symbol) {
  const qtyInput = document.querySelector(`input[id='sell-${CSS.escape(symbol)}']`);
  const quantity = parseInt(qtyInput.value);
  if (!quantity || quantity <= 0 || !portfolio[symbol]) return;

  portfolio[symbol] -= quantity;
  if (portfolio[symbol] <= 0) delete portfolio[symbol];
  updatePortfolioUI();
}

// 🧠 Auto-fill AI
function autofillAI(stock) {
  document.getElementById("questionInput").value = `What is the prediction for ${stock._id}?`;
  currentPrice = stock.price || 100;
  document.getElementById("aiResponse").innerHTML = "";
}

// 📤 Upload
document.getElementById("uploadPortfolio").addEventListener("click", async () => {
  const fileInput = document.getElementById("portfolioFile");
  const file = fileInput.files[0];
  if (!file) return alert("Please upload a file first.");

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/upload", {
    method: "POST",
    body: formData
  });

  const result = await response.json();
  if (result.status === "success") {
    portfolio = result.summary;
    updatePortfolioUI();
  } else {
    alert("Error: " + result.message);
  }
});

// 🔄 Update UI
function updatePortfolioUI() {
  const tableBody = document.getElementById("portfolioSummary");
  const summarySection = document.getElementById("portfolioSummarySection");
  tableBody.innerHTML = "";

  for (const symbol in portfolio) {
    const escapedSymbol = CSS.escape(symbol);
    const quantity = portfolio[symbol];
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${symbol}</td>
      <td>${quantity}</td>
      <td>
        <div class="input-group input-group-sm">
          <input type="number" id="sell-${escapedSymbol}" class="form-control" placeholder="Qty" style="max-width: 60px;">
          <button class="btn btn-sm btn-danger" onclick="sellStock('${symbol}')">Sell</button>
        </div>
      </td>`;
    tableBody.appendChild(row);
  }

  summarySection.style.display = "block";
  const ctx = document.getElementById("portfolioChart").getContext("2d");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: Object.keys(portfolio),
      datasets: [{
        label: "Allocation",
        data: Object.values(portfolio),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#FF9F40', '#9966FF', '#00C49F']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: 2,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            font: { size: 14, family: 'Lato' }
          }
        }
      }
    }
  });

  updatePortfolioMetrics();
}

// 📊 Portfolio metrics
let latestSharpe = 0.0;
function updatePortfolioMetrics() {
  const symbols = Object.keys(portfolio);
  if (symbols.length === 0) {
    document.getElementById("portfolioMetrics").innerHTML = "";
    latestSharpe = 0.0;
    return;
  }

  fetch("/portfolio-metrics", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ portfolio })
  })
    .then(res => res.json())
    .then(data => {
      if (data.status === "success") {
        document.getElementById("portfolioMetrics").innerHTML = `
          <p class="mt-3"><strong>Average Performance:</strong> ${data.average_performance}%</p>
          <p><strong>Estimated Sharpe Ratio:</strong> ${data.sharpe_ratio}</p>
        `;
        latestSharpe = data.sharpe_ratio;
      }
    });
}

// 🤖 Ask AI (✅ corrigé sans `context`)
document.getElementById("aiForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const question = document.getElementById("questionInput").value.trim();
  if (!question) {
    document.getElementById("aiResponse").innerHTML = `<span class="text-danger">Please provide a valid question.</span>`;
    return;
  }

  const sentimentScore = parseFloat(document.getElementById("sentimentResult")?.innerText?.match(/-?\d+(\.\d+)?/)?.[0] || "-0.3");

  const gainers_list = allGainers.map(g => g._id);
  const transactions = "No recent transactions"; // Option à dynamiser plus tard

  const response = await fetch("/ask-llm", {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question,
      sentiment_score: sentimentScore,
      price: currentPrice,
      gainers_list,
      portfolio,
      sharpe_value: latestSharpe,
      transactions
    })
  });

  const data = await response.json();
  if (data.status === "success") {
    document.getElementById("aiResponse").innerHTML = `
      <strong>Answer:</strong> ${data.answer}<br>
      <strong>Sharpe Classification:</strong> ${data.classification}
    `;
  } else {
    document.getElementById("aiResponse").innerHTML = `<span class="text-danger">❌ ${data.message}</span>`;
  }
});

// 📰 Sentiment buttons
document.getElementById("analyzeSentiment").addEventListener("click", async () => {
  const res = await fetch("/analyze-sentiment");
  const data = await res.json();
  updateSentimentUI(data);
});
document.getElementById("analyzeSentimentLocal").addEventListener("click", async () => {
  const res = await fetch("/analyze-news-local");
  const data = await res.json();
  updateSentimentUI(data);
});

// 🧠 Update Sentiment UI
function updateSentimentUI(data) {
  const list = document.getElementById("newsList");
  list.innerHTML = "";
  data.news.forEach(n => {
    list.innerHTML += `<li class='list-group-item'>📰 <a href='${n.url}' target='_blank'>${n.title}</a></li>`;
  });

  document.getElementById("sentimentResult").innerHTML = `Average sentiment score: <strong>${data.avg_score.toFixed(2)}</strong>`;
  let comment = "Neutral.";
  if (data.avg_score > 0) comment = "Positive sentiment detected 📈";
  else if (data.avg_score < 0) comment = "Negative sentiment detected ⚠️";
  document.getElementById("sentimentComment").innerHTML = `<strong>Comment:</strong> ${comment}`;
}

// 📅 Advisor dropdown
document.getElementById("advisorSelect").addEventListener("change", function () {
  const selected = this.value;
  const img = document.getElementById("advisorImage");
  img.src = selected === "Gordon Gekko" ? "/images/gekko.jpg" :
             selected === "Michael Burry" ? "/images/burry.jpg" :
             "/images/dalio.jpg";
  img.style.display = "block";
});

// 📬 Appointment request
document.getElementById("requestAppointment").addEventListener("click", () => {
  const advisor = document.getElementById("advisorSelect").value;
  document.getElementById("advisorResponse").innerHTML =
    `Thank you. Your advisor will contact you shortly to schedule a meeting.`;
});
