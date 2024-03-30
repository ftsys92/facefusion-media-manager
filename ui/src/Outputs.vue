<template>
    <div class="w-full">
        <div class="flex flex-col items-start justify-between p-2 gap-2">
            <div class="flex items-center justify-between w-full">
                <h2 class="text-lg font-bold mb-2 cursor-pointer" @click="show = !show">
                    <span class="text-xs">{{ show ? '&#9660;' : '&#9650;' }}</span> Outputs
                </h2>
                <media-type-select v-model="mediaType" class="w-[150px]"></media-type-select>
            </div>

            <div class="flex items-center justify-between gap-2 self-end">
                <button
                    class="md:hidden rounded-md bg-indigo-600 px-3 py-1 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
                    @click="twoCol = !twoCol">{{ twoCol ? 'One Col' : 'Two Col' }}</button>
                <button
                    class="rounded-md bg-indigo-600 px-3 py-1 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
                    @click="shuffle">Shuffle</button>
                <button
                    class="rounded-md bg-indigo-600 px-3 py-1 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
                    @click="sortDesc">Sort Desc</button>
            </div>
        </div>
        <ul v-show="show" class="grid md:grid-cols-6 gap-5 p-2" :class="{
                    'grid-cols-2': twoCol,
                    'grid-cols-1': !twoCol
                }">
            <li v-for="(file, index) in filteredMediaFiles" :key="index"
                class="flex flex-col relative rounded-md hover:shadow-2xl shadow-xl">
                <div class="flex flex-col">
                    <video v-if="file.url.endsWith('.mp4')" :src="file.url" controls
                        class="bg-black rounded-t-md w-full" :class="{
                    'h-52 sm:h-72': twoCol,
                    'h-auto md:h-52': !twoCol
                }">
                    </video>
                    <img v-if="file.url.endsWith('.png') || file.url.endsWith('.jpg')" :src="file.url"
                        class="rounded-t-md w-full object-cover" @click="toggleFullscreen(file)" :class="{
                    'h-52 sm:h-72': twoCol,
                    'h-auto md:h-52': !twoCol
                }" />
                </div>


                <div class="flex items-center justify-between px-1 py-2">
                    <span class="text-xs text-black font-semibold truncate">
                        {{ file.name }}
                    </span>
                    <div class="flex items-center justify-between gap-1">
                        <span class="select-none text-md md:text-sm cursor-pointer"
                            @click.stop="deleteFile(file.name)">&#128465;</span>
                    </div>
                </div>
            </li>
        </ul>
        <full-screen-media v-if="isFullScreen" :mediaSrc="fullScreenMediaFile" :list="filteredMediaFiles" />
    </div>
</template>
<script setup>
import { onMounted, ref, computed } from 'vue';
import axios from 'axios';
import FullScreenMedia from './FullScreenMedia.vue';
import MediaTypeSelect from './MediaTypeSelect.vue';
import { useNormalizeUrl } from './hooks/useNormalizeUrl';

const props = defineProps({
    source: {
        type: [Object, undefined],
        default: undefined
    }
});

const server = ref(sessionStorage.getItem('server', ''));
const key = ref(sessionStorage.getItem('key') || '');
const show = ref(false);

const twoCol = ref(false);

onMounted(() => {
    fetchMediaFiles();
})

const mediaFiles = ref([]);
const fetchMediaFiles = async () => {
    try {
        const response = await axios(`${useNormalizeUrl(server.value)}/list-output`, {
            headers: {
                Authorization: `Bearer ${key.value}`
            }
        });

        const data = response.data?.data || [];
        mediaFiles.value = data.sort((a, b) => b.name.split('_')[0] - a.name.split('_')[0]);
    } catch (error) {
        console.error('There was an error!', error);
    }
};

const mediaType = ref(null);
const filteredMediaFiles = computed(() => {
    let filtered = mediaFiles.value;

    if (mediaType.value) {
        filtered = filtered.filter((f) => {
            if (mediaType.value === 'image') {
                return f.name.endsWith(`.png`) || f.name.endsWith(`.jpg`);
            } else if (mediaType.value === 'video') {
                return f.name.endsWith(`.mp4`);
            }
        });
    }

    if (props.source) {
        filtered = filtered.filter((f) => {
            const sourceName = f.name.split('_')[1];
            return sourceName === props.source.name.split('.')[0];
        })
    }

    return filtered;
})

const deleteFile = async (fileName) => {
    if (!window.confirm('Are you sure?')) {
        return;
    }

    try {
        await axios(`${useNormalizeUrl(server.value)}/delete_file`, {
            method: 'DELETE',
            headers: {
                Authorization: `Bearer ${key.value}`
            },
            data: {
                name: fileName,
                dir: 'output'
            }
        });

        mediaFiles.value = mediaFiles.value.filter((mf) => mf.name !== fileName);
    } catch (error) {
        console.error('There was an error!', error);
    }
}

const isFullScreen = ref(false);
const fullScreenMediaFile = ref('');
const toggleFullscreen = (file) => {
    fullScreenMediaFile.value = file.url
    isFullScreen.value = true;
};

document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
        isFullScreen.value = false;
        fullScreenMediaFile.value = '';
    }
}, false);

const shuffle = () => {
    mediaFiles.value = mediaFiles.value.sort(() => 0.5 - Math.random());
}
const sortDesc = () => {
    mediaFiles.value = mediaFiles.value.sort((a, b) => b.name.split('_')[0] - a.name.split('_')[0]);
}

defineExpose({
    mediaFiles,
})
</script>