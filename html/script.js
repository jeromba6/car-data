var carId = 'car0';

async function fetchData(jsonFile) {
    const response = await fetch(jsonFile);
    const data = await response.json();
    return data;
}

fetchData('data.json').then(jdata => {
  var dataPoints = [];
  var dataPoints2 = [];
  //var dataPoints3 = [['Tijdstip', 'MB / s', { role: 'style' }]];
  var color = 0;
  var colors = ['red','blue'];
  for (let i = 0; i < jdata[carId].length; i++) {
    let date = new Date(jdata[carId][i]['time'] * 1000);
    dataPoints.push([
      date,
      jdata[carId][i]['odometer']]
    )
    dataPoints2.push([
      date,
      jdata[carId][i]['range'],
      jdata[carId][i]['soc']]
    )
  }
  google.charts.load('current', {packages: ['corechart', 'line']});
  google.charts.setOnLoadCallback(drawBasic);
  google.charts.load('current', {packages: ['corechart', 'line']});
  google.charts.setOnLoadCallback(drawBasic2);

  function drawBasic() {
    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'X');
    data.addColumn('number', 'Total');
    data.addRows(dataPoints);
    var options = {
      title: 'Km driven over time',
      legend: { position: 'none' },
      hAxis: {
        title: 'Time'
      },
      vAxis: {
        title: 'Km driven',
      }
    };
    var chart = new google.visualization.LineChart(document.getElementById('chart1_div'));
    chart.draw(data, options);
  }
  function drawBasic2() {
    var data = new google.visualization.DataTable();
    data.addColumn('datetime', 'X');
    data.addColumn('number', 'Range');
    data.addColumn('number', 'State of charge (%)');
    data.addRows(dataPoints2);
    var options = {
      title: 'Estimated range and state of charge',
      series: {
        0: {targetAxisIndex: 0},
        1: {targetAxisIndex: 1}
        },
      hAxis: {
        title: 'Time'
      },
	          vAxes: {
          // Adds titles to each axis.
          0: {title: 'Range in Km'},
          1: {title: 'State of charge in %'}
        },
    };
    var chart = new google.visualization.LineChart(document.getElementById('chart2_div'));
    chart.draw(data, options);
  }
});


fetchData('km-per-period.json').then(jdata => {
  var dataPointsDay = [['Day', 'KM', { role: 'style' }]];
  var dataPointsWeek = [['Week', 'KM', { role: 'style' }]];
  var dataPointsMonth = [['Month', 'KM', { role: 'style' }]];
  var dataPointsYear = [['Year', 'KM', { role: 'style' }]];

  for (let i = 0; i < jdata['day'][carId].length; i++) {
    dataPointsDay.push([
      jdata['day'][carId][i]['time'],
      jdata['day'][carId][i]['km'],
      'blue'
    ]
    )
  }
  for (let i = 0; i < jdata['week'][carId].length; i++) {
    dataPointsWeek.push([
      jdata['week'][carId][i]['time'],
      jdata['week'][carId][i]['km'],
      'blue'
    ]
    )
  }
  for (let i = 0; i < jdata['month'][carId].length; i++) {
    dataPointsMonth.push([
      jdata['month'][carId][i]['time'],
      jdata['month'][carId][i]['km'],
      'blue'
    ]
    )
  }
  for (let i = 0; i < jdata['year'][carId].length; i++) {
    dataPointsYear.push([
      jdata['year'][carId][i]['time'],
      jdata['year'][carId][i]['km'],
      'blue'
    ]
    )
  }

  google.charts.load('current', {packages: ['corechart', 'line']});
  google.charts.setOnLoadCallback(drawBasicDay);
  google.charts.setOnLoadCallback(drawBasicWeek);
  google.charts.setOnLoadCallback(drawBasicMonth);
  google.charts.setOnLoadCallback(drawBasicYear);

  function drawBasicDay() {
    var data = google.visualization.arrayToDataTable(dataPointsDay);
    var options = {
      title: 'KM per day',
      legend: { position: 'none' },
      hAxis: {
        title: 'Day'
      },
      vAxis: {
        title: 'Km driven',
        logScale: false
      }
    };

    var chart = new google.visualization.ColumnChart(document.getElementById('chart_day'));
    chart.draw(data, options);
  }

  function drawBasicWeek() {
    var data = google.visualization.arrayToDataTable(dataPointsWeek);
    var options = {
      title: 'KM per week',
      legend: { position: 'none' },
      hAxis: {
        title: 'Week'
      },
      vAxis: {
        title: 'Km driven',
        logScale: false
      }
    };

    var chart = new google.visualization.ColumnChart(document.getElementById('chart_week'));
    chart.draw(data, options);
  }

  function drawBasicMonth() {
    var data = google.visualization.arrayToDataTable(dataPointsMonth);
    var options = {
      title: 'KM per month',
      legend: { position: 'none' },
      hAxis: {
        title: 'Month'
      },
      vAxis: {
        title: 'Km driven',
        logScale: false
      }
    };

    var chart = new google.visualization.ColumnChart(document.getElementById('chart_month'));
    chart.draw(data, options);
  }

  function drawBasicYear() {
    var data = google.visualization.arrayToDataTable(dataPointsYear);
    var options = {
      title: 'KM per year',
      legend: { position: 'none' },
      hAxis: {
        title: 'Year'
      },
      vAxis: {
        title: 'Km driven',
        logScale: false
      }
    };

    var chart = new google.visualization.ColumnChart(document.getElementById('chart_year'));
    chart.draw(data, options);
  }
});
