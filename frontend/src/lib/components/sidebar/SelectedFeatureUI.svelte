<script>
    import ChatElement from "$lib/components/sidebar/ChatElement.svelte";
    import BentoBox from "$lib/components/sidebar/BentoBox.svelte"
    const allowedProperties = [
        "Operator (or Applicant)",
        "Site Name",
        "Technology Type",
        "Installed Capacity (MWelec)",
        "Development Status",
        "Planning Permission Refused",
        "Planning Application Withdrawn",
        "Planning Application Submitted",
    ];
    export let councils = null;
    export let selectedFeature = null;
    export let nimby_choice = null;
    export let resetSelection;
    export let nimbyRadarCanvas;

    let buttonText = "Copy Ref";
    console.log("nimby Choice:", nimby_choice)
    console.log("Selected Feature:", selectedFeature);
    const copyToClipboard = () => {
        let copy = selectedFeature.properties["Planning Application Reference"];
        navigator.clipboard.writeText(copy).then(() => {
            buttonText = "Copied!";
            setTimeout(() => {
                buttonText = "Copy Ref";
            }, 2000); // Revert the button text after 2 seconds
        });
    };
</script>

<div class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden animate-fade-in">
    <div class="border-b border-gray-100 px-6 py-4 bg-gradient-to-r from-gray-50 to-white">
        <button class="inline-flex items-center text-sm text-gray-600 hover:text-orange-600 transition-colors mb-3 group">
            <svg class="w-4 h-4 mr-1.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
            </svg>
            <span on:click={resetSelection} >Back to overview</span>
        </button>
        
        <h2 class="text-lg font-semibold text-gray-900">
            {selectedFeature.properties["Site Name"]}
        </h2>
    </div>
    <div class="px-6 py-4 space-y-4">
        <!-- Authority and Reference Section -->
        <div class="space-y-3">
            <div class="flex items-start justify-between">
                <span class="text-sm text-gray-500">Planning Authority</span>
                <span class="text-sm font-medium text-gray-900 text-right">{selectedFeature.properties["Planning Authority"]}</span>
            </div>
        </div>
        <div class="flex items-start justify-between">
            <span class="text-sm text-gray-500">Reference</span>
            <div class="text-right">
                <span class="text-sm font-mono font-medium text-gray-900">{selectedFeature.properties["Planning Application Reference"]}</span>
                <button  on:click={copyToClipboard} class="ml-2 inline-flex items-center justify-center w-6 h-6 rounded hover:bg-gray-100 transition-colors group">
                    <svg class="w-4 h-4 text-gray-400 group-hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>

                </button>
            </div>
        </div>
        <div class="flex items-start justify-between">
            <span class="text-sm text-gray-500">Submitted</span>
            <span class="text-sm text-gray-900">{selectedFeature.properties["Planning Application Submitted"]}</span>
        </div>

        <div class="space-y-2 pt-2">
            <a         href={councils[selectedFeature.properties["Planning Authority"]]}
 class="w-full inline-flex items-center justify-center px-4 py-2.5 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-all group">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                </svg>
                View Planning Database (Copy Reference)
            </a>

            <a  href={nimby_choice["article_url"]} class="w-full inline-flex items-center justify-center px-4 py-2.5 border border-orange-200 text-sm font-medium rounded-md text-orange-700 bg-orange-50 hover:bg-orange-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-all group">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                View Possible Article
            </a>
        </div>
    </div>
    <BentoBox data={selectedFeature.properties}/>

    <!-- {#if selectedFeature.properties["Planning Permission Refused"] != 0}
        <p class="text-xs">
            Refused: {selectedFeature.properties["Planning Permission Refused"]}
        </p>
    {/if}

    {#if selectedFeature.properties["Planning Permission Withdraw"] != 0}
        <p class="text-xs">
            Withdrawn: {selectedFeature.properties[
                "Planning Permission Withdrawn"
            ]}
        </p>
    {/if}
    <p class="text-xs font-bold">
        Record Last Updated {selectedFeature.properties[
            "Record Last Updated (dd/mm/yyyy)"
        ]}
    </p> -->
</div>
{#if nimby_choice}

    <div class="bg-white rounded-xl gap-4 mt-2 mb-2"  bind:this={sidebarContent}>
        <hr />
        <ul class="list bg-base-100 rounded-box shadow-md mt-2 mb-2">
            <li class="p-4 pb-2 text-xs opacity-60 tracking-wide">
                3 'Fun' Facts about this Failure
            </li>

            {#each nimby_choice["Interesting Tidbits"] || [] as tidbit}
                <li class="list-row p-4">
                    <div class="list-col-grow text-sm">
                        {tidbit}
                    </div>
                </li>
            {/each}
        </ul>
        <ChatElement chats={[nimby_choice["header"], nimby_choice["Snide Commentary"]]}/>

    </div>

    <div class="flex mt-5 justify-center items-center">

    </div>
{/if}
