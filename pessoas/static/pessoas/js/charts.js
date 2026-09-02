(() => {
  const canvas = document.getElementById('chartPessoas');
  const dataElement = document.getElementById('chart-data');
  if (!canvas || !dataElement || typeof Chart === 'undefined') {
    return;
  }

  const chartData = JSON.parse(dataElement.textContent);
  const isCircular = chartData.type === 'doughnut';
  const dataset = {data: chartData.values};
  if (chartData.type === 'line') {
    dataset.tension = 0.25;
  }

  const options = isCircular
    ? {plugins: {legend: {labels: {color: '#fff'}}}}
    : {
        scales: {
          x: {ticks: {color: '#fff'}, grid: {color: 'rgba(255,255,255,.08)'}},
          y: {ticks: {color: '#fff'}, grid: {color: 'rgba(255,255,255,.08)'}},
        },
        plugins: {legend: {display: false}},
      };

  new Chart(canvas, {
    type: chartData.type,
    data: {labels: chartData.labels, datasets: [dataset]},
    options,
  });
})();
