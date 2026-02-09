<script>
    export let chats = []
    let isTyping = false
    let displayedChats = []
    async function animateChats() {
        displayedChats = []
        
        for (let i = 0; i < chats.length; i++) {
            isTyping = true
            await new Promise(resolve => setTimeout(resolve, 1200))
            
            isTyping = false
            displayedChats = [...displayedChats, chats[i]]
            
            if (i < chats.length - 1) {
                await new Promise(resolve => setTimeout(resolve, 400))
            }
        }
    }
    $: if (chats.length > 0) animateChats()

</script>
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
    <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-amber-400 flex items-center justify-center text-white font-bold text-sm shadow-md">
                CEG
            </div>
        </div>
        <div class="flex-1 space-y-2">
            {#each displayedChats  as chat}
            <div class="bg-gradient-to-r from-orange-100 to-amber-100 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
                <p class="text-sm text-gray-800">{chat}</p>
            </div>
            {/each}
            {#if isTyping}
            <div class="animate-in slide-in-from-left-2 fade-in duration-300 bg-gradient-to-r from-orange-100 to-amber-100 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
                <div class="flex space-x-1">
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]"></div>
                    <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]"></div>
                </div>
            </div>
            {/if}
            
            <p class="text-xs text-gray-500 mt-2 ml-2">Analysis by C.E.G - He may be wrong!</p>
        </div>
    </div>
</div>