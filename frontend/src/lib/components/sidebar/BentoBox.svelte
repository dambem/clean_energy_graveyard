<script>

export let data = null
  import { Zap, Battery } from '@lucide/svelte';
    const allowedProperties = [
        "Operator (or Applicant)",
        "Site Name",
        "Development Status",
        "Planning Permission Refused",
        "Planning Application Withdrawn",
        "Planning Application Submitted",
    ];
  console.log(data)
</script>
    <div class="max-w-4xl mx-auto">
        <!-- Two Main Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-2 m-2">
            <!-- MW Capacity Card -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div class="flex items-start justify-between">
                    <div>
                        <p class="text-sm text-gray-500 mb-1">Capacity</p>
                        <div class="flex items-baseline gap-2">
                            <span class="text-xl font-bold text-gray-900">{data['Installed Capacity (MWelec)']}</span>
                            <span class="text-lg text-gray-600">MW</span>
                        </div>
                        <p class="text-xs text-gray-500 mt-2">Installed capacity</p>
                    </div>
                    <div class="p-2 bg-blue-100 rounded-lg">
                        <Battery class="w-6 h-6 text-blue-600"/>
                    </div>
                </div>
            </div>

            <!-- Technology Type Card -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div class="flex items-start justify-between">
                    <div>
                        <p class="text-sm text-gray-500 mb-1">Technology</p>
                        <p class="text-xl font-bold text-gray-900">{data['Technology Type']}</p>
                        <p class="text-xs text-gray-500 mt-2">Type</p>
                    </div>
                    <div class="p-2 bg-amber-100 rounded-lg">
                        <Zap class="w-6 h-6 text-amber-600"/>
                    </div>
                </div>
            </div>

        </div>
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden m-2">
            <details class="group">
                <summary class="px-6 py-4 cursor-pointer hover:bg-gray-50 transition-colors flex items-center justify-between">
                    <span class="text-sm font-medium text-gray-700">View all property details</span>
                    <i data-lucide="chevron-down" class="w-5 h-5 text-gray-400 group-open:rotate-180 transition-transform"></i>
                </summary>
                
                <div class="border-t border-gray-200">
                    <table class="w-full">
                        <tbody class="divide-y divide-gray-200">
                            {#each Object.entries(data).filter( ([key]) => allowedProperties.includes(key), ) as [key, value]}
                                {#if key !== "title"}
                                    <tr class="hover:bg-gray-50 transition-colors">
                                        <td class="px-6 py-3 text-sm font-medium text-gray-600">{key.replace(/_/g, " ")}</td>
                                        <td class="px-6 py-3 text-sm text-gray-900 text-right">{value}</td>
                                    </tr>
                                {/if}
                            {/each}

                        </tbody>
                    </table>
                </div>
            </div>
        </div>