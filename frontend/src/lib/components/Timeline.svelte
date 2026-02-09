<script>
  import { createEventDispatcher } from 'svelte';
  
  export let startDate = '';
  export let endDate = '';
  export let minDate = '2020-01-01';
  export let maxDate = '2024-12-31';
  
  const dispatch = createEventDispatcher();
  
  let isDragging = false;
  let dragTarget = null;
  let sliderRef;
  
  // Convert date string to timestamp for calculations
  function dateToTimestamp(dateStr) {
    return new Date(dateStr).getTime();
  }
  
  // Convert timestamp back to date string
  function timestampToDate(timestamp) {
    return new Date(timestamp).toISOString().split('T')[0];
  }
  
  // Get position percentage for a date
  function getPositionPercent(dateStr) {
    const timestamp = dateToTimestamp(dateStr);
    const minTimestamp = dateToTimestamp(minDate);
    const maxTimestamp = dateToTimestamp(maxDate);
    return ((timestamp - minTimestamp) / (maxTimestamp - minTimestamp)) * 100;
  }
  
  // Get date from position percentage
  function getDateFromPercent(percent) {
    const minTimestamp = dateToTimestamp(minDate);
    const maxTimestamp = dateToTimestamp(maxDate);
    const timestamp = minTimestamp + (percent / 100) * (maxTimestamp - minTimestamp);
    return timestampToDate(timestamp);
  }
  
  // Handle mouse/touch events
  function handlePointerDown(e, target) {
    isDragging = true;
    dragTarget = target;
    e.preventDefault();
  }
  
  function handlePointerMove(e) {
    if (!isDragging || !sliderRef) return;
    
    const rect = sliderRef.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percent = Math.max(0, Math.min(100, (x / rect.width) * 100));
    const newDate = getDateFromPercent(percent);
    
    if (dragTarget === 'start') {
      startDate = newDate;
      // Ensure start date doesn't go past end date
      if (dateToTimestamp(startDate) > dateToTimestamp(endDate)) {
        endDate = startDate;
      }
    } else {
      endDate = newDate;
      // Ensure end date doesn't go before start date
      if (dateToTimestamp(endDate) < dateToTimestamp(startDate)) {
        startDate = endDate;
      }
    }
    
    dispatch('change', { startDate, endDate });
  }
  
  function handlePointerUp() {
    isDragging = false;
    dragTarget = null;
  }
  
  // Format date for display
  function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  }
  
  // Initialize default dates if not provided
  if (!startDate) startDate = minDate;
  if (!endDate) endDate = maxDate;
  
  $: startPercent = getPositionPercent(startDate);
  $: endPercent = getPositionPercent(endDate);
</script>

<svelte:window 
  on:pointermove={handlePointerMove}
  on:pointerup={handlePointerUp}
/>

<div class="timeline-container">
  <div class="timeline-wrapper">
    <!-- Date labels -->
    <div class="date-labels">
      <div class="date-label start" style="left: {startPercent}%">
        {formatDate(startDate)}
      </div>
      <div class="date-label end" style="left: {endPercent}%">
        {formatDate(endDate)}
      </div>
    </div>
    
    <!-- Timeline track -->
    <div class="timeline-track" bind:this={sliderRef}>
      <!-- Background track -->
      <div class="track-bg"></div>
      
      <!-- Active range -->
      <div 
        class="track-active" 
        style="left: {startPercent}%; width: {endPercent - startPercent}%"
      ></div>
      
      <!-- Start handle -->
      <div 
        class="handle start-handle" 
        style="left: {startPercent}%"
        on:pointerdown={(e) => handlePointerDown(e, 'start')}
        role="slider"
        tabindex="0"
        aria-label="Start date"
      ></div>
      
      <!-- End handle -->
      <div 
        class="handle end-handle" 
        style="left: {endPercent}%"
        on:pointerdown={(e) => handlePointerDown(e, 'end')}
        role="slider"
        tabindex="0"
        aria-label="End date"
      ></div>
    </div>
    
    <!-- Min/Max date labels -->

    <!-- Info text -->

  </div>
</div>

<style>
  .timeline-container {
    position: absolute;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 300px;
    background: rgba(90, 90, 90, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 5px;
    padding-right: 50px;
    padding-left: 50px;

    border: 1px solid rgba(255, 255, 255, 0.2);
    z-index: 1000;
  }
  
  .timeline-wrapper {
    position: relative;
    width: 100%;
  }
  
  .date-labels {
    position: relative;
    height: 60px;
    margin-bottom: 15px;
  }
  
  .date-label {
    position: absolute;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.2);
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: rgba(255, 255, 255, 0.95);
    padding: 6px 12px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
    pointer-events: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .date-label.start {
    top: 0;
    background: rgba(232, 148, 12, 0.3);
    border-color: rgba(232, 148, 12, 0.786);
  }
  
  .date-label.end {
    bottom: 0;
    background: rgba(232, 148, 12, 0.3);
    border-color: rgba(232, 148, 12, 0.786);  }
  
  .timeline-track {
    position: relative;
    height: 12px;
    margin: 15px 0;
    cursor: pointer;
    border-radius: 6px;
    overflow: hidden;
  }
  
  .track-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 100%;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    backdrop-filter: blur(3px);
  }
  
  .track-active {
    position: absolute;
    top: 0;
    height: 100%;
    background: linear-gradient(90deg, 
      rgba(246, 62, 38, 0.4) 0%, 
      rgba(185, 160, 16, 0.6) 25%,
      rgba(239, 173, 68, 0.6) 75%, 
      rgba(236, 113, 12, 0.4) 100%
    );
    border-radius: 6px;
    transition: all 0.1s ease;
    backdrop-filter: blur(2px);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .handle {
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%);
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, 0.6);
    cursor: grab;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(5px);
  }
  
  .handle:hover {
    transform: translate(-50%, -50%) scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    border-color: rgba(255, 255, 255, 0.8);
  }
  
  .handle:active {
    cursor: grabbing;
    transform: translate(-50%, -50%) scale(0.95);
  }
  
  .start-handle {
    background: rgba(232, 148, 12, 0.3);
    border-color: rgba(108, 59, 36, 0.6);
  }
  
  .start-handle:hover {
    background: rgba(15, 92, 237, 0.4);
    border-color: white;
  }
  
  .end-handle {
    background: rgba(232, 148, 12, 0.3);
    border-color: rgba(108, 59, 36, 0.6);
  }
  
  .end-handle:hover {
    background: rgba(15, 92, 237, 0.4);
    border-color: white;
  }
  
  .timeline-labels {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
  }
  
  .timeline-info {
    text-align: center;
    color: rgba(255, 255, 255, 0.6);
    font-size: 11px;
    margin-top: 8px;
    font-weight: 400;
  }
  
  /* Mobile responsiveness */
  @media (max-width: 640px) {
    .timeline-container {
      width: 95%;
      padding: 12px;
    }
    
    .handle {
      width: 28px;
      height: 28px;
    }
    
    .date-label {
      font-size: 12px;
      padding: 5px 10px;
    }
    
    .timeline-track {
      height: 14px;
    }
  }
</style>