<script>
  import { onMount } from 'svelte';
  
  // Props
  export let totalCards = 12;
  export let cardsVisible = 7;
  export let cardWidth = 95; // 80px card + 15px gap
  
  // State
  let currentIndex = totalCards; // Start at middle set
  let isScrolling = false;
  let carouselContainer;
  let carouselTrack;
  
  // Reactive values
  $: translateX = -currentIndex * cardWidth;
  $: realIndex = currentIndex % totalCards;
  
  // Create cards array (3 sets for infinite scrolling)
  $: cards = Array(3).fill().flatMap((_, setIndex) => 
    Array(totalCards).fill().map((_, cardIndex) => ({
      id: `${setIndex}-${cardIndex}`,
      index: cardIndex,
      setIndex
    }))
  );
  
  // Create dots array
  $: dots = Array(totalCards).fill().map((_, i) => i);
  
  // Calculate card transforms for arc effect
  function getCardTransform(cardGlobalIndex) {
    const relativeIndex = cardGlobalIndex - currentIndex - Math.floor(cardsVisible / 2);
    const angle = relativeIndex * 8; // degrees
    const distance = Math.abs(relativeIndex);
    const yOffset = Math.pow(distance, 1.5) * 3;
    const opacity = Math.max(0.3, 1 - (distance * 0.15));
    const zIndex = Math.max(1, 10 - distance);
    
    return {
      transform: `translateY(${yOffset}px) rotate(${angle}deg)`,
      opacity,
      zIndex
    };
  }
  
  // Navigation functions
  function prev() {
    currentIndex--;
    handleInfiniteScroll();
  }
  
  function next() {
    currentIndex++;
    handleInfiniteScroll();
  }
  
  function goTo(index) {
    const diff = index - realIndex;
    currentIndex += diff;
    handleInfiniteScroll();
  }
  
  // Handle infinite scrolling
  function handleInfiniteScroll() {
    const totalCreatedCards = cards.length;
    const buffer = totalCards;
    
    setTimeout(() => {
      if (currentIndex < buffer) {
        currentIndex += totalCards;
        if (carouselTrack) {
          carouselTrack.style.transition = 'none';
          setTimeout(() => {
            carouselTrack.style.transition = 'transform 0.3s ease';
          }, 10);
        }
      } else if (currentIndex >= totalCreatedCards - buffer) {
        currentIndex -= totalCards;
        if (carouselTrack) {
          carouselTrack.style.transition = 'none';
          setTimeout(() => {
            carouselTrack.style.transition = 'transform 0.3s ease';
          }, 10);
        }
      }
    }, 300);
  }
  
  // Event handlers
  function handleWheel(e) {
    e.preventDefault();
    if (isScrolling) return;
    
    isScrolling = true;
    
    if (e.deltaY > 0) {
      next();
    } else {
      prev();
    }
    
    setTimeout(() => {
      isScrolling = false;
    }, 100);
  }
  
  function handleKeydown(e) {
    if (e.key === 'ArrowLeft') prev();
    if (e.key === 'ArrowRight') next();
  }
  
  // Touch handling
  let startX = 0;
  let isDragging = false;
  
  function handleTouchStart(e) {
    startX = e.touches[0].clientX;
    isDragging = true;
  }
  
  function handleTouchMove(e) {
    if (!isDragging) return;
    e.preventDefault();
  }
  
  function handleTouchEnd(e) {
    if (!isDragging) return;
    
    const endX = e.changedTouches[0].clientX;
    const diff = startX - endX;
    
    if (Math.abs(diff) > 50) {
      if (diff > 0) next();
      else prev();
    }
    
    isDragging = false;
  }
  
  onMount(() => {
    document.addEventListener('keydown', handleKeydown);
    
    return () => {
      document.removeEventListener('keydown', handleKeydown);
    };
  });
</script>

<div class="carousel-container" bind:this={carouselContainer} on:wheel={handleWheel}>
  <div class="carousel-wrapper">
    <div 
      class="carousel-track" 
      bind:this={carouselTrack}
      style="transform: translateX({translateX}px)"
      on:touchstart={handleTouchStart}
      on:touchmove={handleTouchMove}
      on:touchend={handleTouchEnd}
    >
      {#each cards as card, index (card.id)}
        <div 
          class="card"
          style="
            {getCardTransform(index).transform}; 
            opacity: {getCardTransform(index).opacity}; 
            z-index: {getCardTransform(index).zIndex};
          "
        >
          <div class="card-inner"></div>
          <div class="card-corner"></div>
        </div>
      {/each}
    </div>
  </div>
  
  <div class="carousel-nav">
    <button class="nav-btn" on:click={prev}>‹</button>
    <div class="carousel-dots">
      {#each dots as dot, index}
        <div 
          class="dot" 
          class:active={index === realIndex}
          on:click={() => goTo(index)}
        ></div>
      {/each}
    </div>
    <button class="nav-btn" on:click={next}>›</button>
  </div>
  
  <div class="carousel-info">
    <span>{realIndex + 1} / {totalCards}</span>
  </div>
</div>

<style>
  .carousel-container {
    position: absolute;
    bottom: 1rem;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 600px;
    background: rgba(90, 90, 90, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
  }

  .carousel-wrapper {
    position: relative;
    overflow: hidden;
    border-radius: 25%;
    height: 140px;
    mask: linear-gradient(90deg, transparent 0%, black 15%, black 85%, transparent 100%);
    -webkit-mask: linear-gradient(90deg, transparent 0%, black 15%, black 85%, transparent 100%);
  }

  .carousel-track {
    display: flex;
    transition: transform 0.3s ease;
    gap: 15px;
    padding: 10px 0;
    transform-origin: center bottom;
  }

  .card {
    flex: 0 0 80px;
    height: 110px;
    background: #e0e0e0;
    border-radius: 8px;
    border: 2px solid #d0d0d0;
    position: relative;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transform-origin: center bottom;
  }

  .card:hover {
    transform: translateY(-8px) scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
    border-color: #bbb;
    z-index: 100 !important;
  }

  .card-inner {
    position: absolute;
    top: 8px;
    left: 8px;
    right: 8px;
    bottom: 8px;
    background: linear-gradient(45deg, #f5f5f5, #e8e8e8);
    border-radius: 4px;
    border: 1px solid #ccc;
  }

  .card-corner {
    position: absolute;
    top: 15px;
    left: 15px;
    width: 12px;
    height: 16px;
    background: #999;
    border-radius: 2px;
    opacity: 0.3;
  }

  .carousel-nav {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 15px;
  }

  .nav-btn {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    color: white;
    font-size: 18px;
    backdrop-filter: blur(5px);
  }

  .nav-btn:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.05);
  }

  .carousel-dots {
    display: flex;
    justify-content: center;
    gap: 8px;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .dot.active {
    background: white;
    transform: scale(1.2);
  }

  .carousel-info {
    text-align: center;
    color: rgba(255, 255, 255, 0.8);
    font-size: 12px;
    margin-top: 10px;
  }
</style>