<script>
  import { onMount, onDestroy } from 'svelte';
  import { Chart, registerables } from 'chart.js';
  
  // Register Chart.js components
  Chart.register(...registerables);
  
  export let delayData = null;

  // Generate sample data for testing
  const generateData = () => {
    const years = [];
    const currentYear = new Date().getFullYear();
    const startYear = currentYear - 5;
    
    for (let i = 0; i < 6; i++) {
      const year = startYear + i;
      const avgDelay = Math.round((Math.random() * 10 + 5) * 10) / 10;
      
      const distribution = [
        { range: '0-5 min', count: Math.floor(Math.random() * 200 + 50) },
        { range: '5-10 min', count: Math.floor(Math.random() * 300 + 100) },
        { range: '10-15 min', count: Math.floor(Math.random() * 250 + 80) },
        { range: '15-20 min', count: Math.floor(Math.random() * 150 + 40) },
        { range: '20+ min', count: Math.floor(Math.random() * 100 + 20) }
      ];
      
      years.push({ year, avgDelay, distribution });
    }
    return years;
  };

  // Create all-time distribution by combining all years
  const calculateAllTimeDistribution = (data) => {
    const allTimeDistribution = [
      { range: '0-90 days', count: 0 },
      { range: '90-180 days', count: 0 },
      { range: '180-365 days', count: 0 },
      { range: '1 Year - 2 Years', count: 0 },
      { range: 'Over 2 Years', count: 0 }
    ];
    
    data.forEach(yearData => {
      yearData.distribution.forEach((item, index) => {
        allTimeDistribution[index].count += item.count;
      });
    });
    
    return allTimeDistribution;
  };

  // State variables
  let data = [];
  let selectedYear = null;
  let showAllTime = false;
  let currentView = 'overview'; // 'overview' or 'distribution'
  let chartTitle = '';
  
  // Chart references
  let barChartCanvas;
  let distributionChartCanvas;
  let barChart = null;
  let distributionChart = null;

  // Chart.js configuration for bar chart
  const createBarChartConfig = (data) => ({
    type: 'bar',
    data: {
      labels: data.map(d => d.year.toString()),
      datasets: [{
        label: 'Average Delay (days)',
        data: data.map(d => d.avgDelay),
        backgroundColor: '#eb8e47',
        borderColor: '#b62121',
        borderWidth: 2,
        borderRadius: 4,
        borderSkipped: false,
        hoverBackgroundColor: '#b62121',
        hoverBorderColor: '#8b1538',
        hoverBorderWidth: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 1000,
        easing: 'easeOutElastic'
      },
      interaction: {
        intersect: false,
        mode: 'index'
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.parsed.y} days average delay`;
            }
          },
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: '#eb8e47',
          borderWidth: 1
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Avg Delay (days)',
            color: '#374151',
            font: {
              size: 14,
              weight: 600
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: '#374151',
            font: {
              size: 12,
              weight: 500
            }
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: '#374151',
            font: {
              size: 12,
              weight: 500
            }
          }
        }
      },
      onClick: (event, activeElements) => {
        if (activeElements.length > 0) {
          const index = activeElements[0].index;
          const yearData = data[index];
          handleBarClick(yearData);
        }
      },
      onHover: (event, activeElements) => {
        event.native.target.style.cursor = activeElements.length > 0 ? 'pointer' : 'default';
      }
    }
  });

  // Chart.js configuration for distribution chart
  const createDistributionChartConfig = (distributionData) => ({
    type: 'line',
    data: {
      labels: distributionData.map(d => d.range),
      datasets: [{
        label: 'Number of Occurrences',
        data: distributionData.map(d => d.count),
        fill: true,
        backgroundColor: 'rgba(235, 142, 71, 0.3)',
        borderColor: '#eb8e47',
        borderWidth: 3,
        pointBackgroundColor: '#eb8e47',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointHoverBackgroundColor: '#b62121',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 3,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 500,
        easing: 'easeOutQuart'
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `${context.parsed.y} occurrences`;
            }
          },
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: '#eb8e47',
          borderWidth: 1
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Occurrences',
            color: '#374151',
            font: {
              size: 14,
              weight: 600
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            color: '#374151',
            font: {
              size: 12,
              weight: 500
            }
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            color: '#374151',
            font: {
              size: 10,
              weight: 500
            },
            maxRotation: 45
          }
        }
      }
    }
  });

  // Handle bar click with smooth transition
  function handleBarClick(entry) {
    if (currentView === 'distribution') return;
    
    // Animate out the bar chart
    if (barChart) {
      barChart.destroy();
      barChart = null;
    }
    
    // Switch to distribution view
    currentView = 'distribution';
    showAllTime = false;
    selectedYear = entry.year;
    
    const yearData = data.find(d => d.year === entry.year);
    if (yearData) {
      chartTitle = `Delay Distribution for ${entry.year}`;
      
      // Small delay for smooth transition
      setTimeout(() => {
        renderDistributionChart(yearData.distribution);
      }, 100);
    }
  }

  // Handle back to overview
  function handleBackToOverview() {
    if (currentView === 'overview') return;
    
    // Destroy distribution chart
    if (distributionChart) {
      distributionChart.destroy();
      distributionChart = null;
    }
    
    // Switch back to overview
    currentView = 'overview';
    selectedYear = null;
    showAllTime = false;
    chartTitle = '';
    
    // Small delay for smooth transition
    setTimeout(() => {
      renderBarChart();
    }, 100);
  }

  // Handle all-time click
  function handleAllTimeClick() {
    if (currentView === 'distribution') return;
    
    // Animate out the bar chart
    if (barChart) {
      barChart.destroy();
      barChart = null;
    }
    
    // Switch to distribution view
    currentView = 'distribution';
    selectedYear = null;
    showAllTime = true;
    chartTitle = 'All-Time Delay Distribution';
    
    const allTimeData = calculateAllTimeDistribution(data);
    
    // Small delay for smooth transition
    setTimeout(() => {
      renderDistributionChart(allTimeData);
    }, 100);
  }

  // Render bar chart
  function renderBarChart() {
    if (!barChartCanvas || !data.length) return;
    
    const ctx = barChartCanvas.getContext('2d');
    const config = createBarChartConfig(data);
    
    barChart = new Chart(ctx, config);
  }

  // Render distribution chart
  function renderDistributionChart(distributionData) {
    if (!distributionChartCanvas || !distributionData.length) return;
    
    const ctx = distributionChartCanvas.getContext('2d');
    const config = createDistributionChartConfig(distributionData);
    
    distributionChart = new Chart(ctx, config);
  }

  // Initialize
  onMount(() => {
    data = delayData || generateData();
    
    // Initial render
    setTimeout(() => {
      renderBarChart();
    }, 100);
  });

  // Cleanup
  onDestroy(() => {
    if (barChart) {
      barChart.destroy();
    }
    if (distributionChart) {
      distributionChart.destroy();
    }
  });
</script>

<div class="container">
  <div class="header">
    <h3 class="chart-title">
      {#if currentView === 'overview'}
        Avg Delay Before Death
      {:else}
        {chartTitle}
      {/if}
    </h3>
    
    {#if currentView === 'overview'}
      <button class="action-btn" on:click={handleAllTimeClick}>
        View All-Time Distribution
      </button>
    {:else}
      <button class="action-btn" on:click={handleBackToOverview}>
        Back to Overview
      </button>
    {/if}
  </div>

  <div class="charts-container">
    <div 
      class="chart-wrapper"
      class:visible={currentView === 'overview'}
    >
      <canvas bind:this={barChartCanvas}></canvas>
    </div>
    
    <div 
      class="chart-wrapper"
      class:visible={currentView === 'distribution'}
    >
      <canvas bind:this={distributionChartCanvas}></canvas>
    </div>
  </div>
</div>

<style>
  .container {
    width: 100%;
    max-width: 100%;
    padding: 1rem;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .chart-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #374151;
    margin: 0;
  }

  .action-btn {
    background: linear-gradient(135deg, #eb8e47 0%, #eb8e47 100%);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .action-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    background: linear-gradient(135deg, #eb8e47 0%, #eb8e47 100%);
  }

  .action-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .charts-container {
    position: relative;
    width: 100%;
    height: 10em;
    min-height: 10em;
  }

  .chart-wrapper {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    padding: 1rem;
    box-sizing: border-box;
  }

  .chart-wrapper.visible {
    opacity: 1;
    visibility: visible;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .container {
      padding: 0.5rem;
    }
    
    .header {
      flex-direction: column;
      align-items: stretch;
    }
    
    .chart-title {
      text-align: center;
      font-size: 1rem;
    }
    
    .action-btn {
      width: 100%;
      text-align: center;
    }
    
    .charts-container {
      height: 350px;
    }
    
    .chart-wrapper {
      padding: 0.5rem;
    }
  }

  @media (max-width: 480px) {
    .charts-container {
      height: 300px;
    }
    
    .chart-title {
      font-size: 0.9rem;
    }
    
    .action-btn {
      font-size: 0.8rem;
      padding: 0.4rem 0.8rem;
    }
  }
</style>