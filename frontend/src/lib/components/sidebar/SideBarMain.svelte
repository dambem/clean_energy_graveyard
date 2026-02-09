<script>
    export let refused = [];
    export let stats = null;
    import About from '$lib/components/About.svelte';
    import DelayTimesVisualization from '$lib/components/DelayTimesVisualization.svelte';
</script>

<div class="glass3d2 flex bg-white rounded-xl p-4 shadow-md">
    <div class="ml-1">
        <h1 class="text-xl font-semibold text-gray-900">Clean Energy Graveyard (C.E.G)</h1>
        <a class="text-sm font-medium text-gray-900" href="https://www.bemben.co.uk">Made by Damian Bemben</a>
    </div>
</div>
<div class="grid grid-cols-2 gap-2" >
    {#each stats as stat}
        <div
            class="bg-white stat place-items-center shadow bg-base-100 rounded-xl"
        >
            <div class=" stat-title">{stat.label}</div>
            <span class="stat-detail stat-value">{stat.value}</span>
            <span class="stat-desc">{stat.trend}</span>
        </div>
    {/each}
</div>
<div class="bg-white rounded-xl p-4 shadow-md mt-2">
    <DelayTimesVisualization delayData={refused} />
</div>
<About />
