<template>
    <div class="w-full p-2">
        <div class="flex flex-col items-start justify-between gap-2">
            <div class="flex items-start justify-between w-full">
                <h2 class="text-lg font-bold mb-2 cursor-pointer" @click="show = !show">
                    Targets <span class="text-xs">{{ selected.length }}</span>
                </h2>
                <div class="flex flex-col items-end md:flex-row  md:items-center gap-1">
                    <media-type-select v-model="mediaType" class="w-[150px]"></media-type-select>
                    <button
                        class="rounded-md bg-indigo-600 px-3 py-1 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
                        @click="() => {
                    if (selected.length) {
                        selected = []
                    } else {
                        selected = filteredTargets
                    }
                }">{{ selected.length ? 'Des. all' : 'Sel. all' }}</button>
                </div>
            </div>
            <div class="flex flex-col items-start justify-between gap-2 w-full md:flex-row md:items-center">
                <input
                    class="rounded-md flex-grow w-full appearance-none bg-white px-1 text-base text-slate-900 placeholder:text-slate-600 focus:outline-none sm:text-sm sm:leading-6 border"
                    v-model="commandArgs" placeholder="Enter args" />
                <div class="flex items-center gap-2">
                    <input type="checkbox" id="face_enhancer" name="face_enhancer" v-model="faceEnhancer" />
                    <label for="face_enhancer">Face Enhancer</label>
                </div>
            </div>
        </div>
        <div v-show="show" class="flex flex-col items-center gap-2 w-full p-1">
            <media-upload ref="mediaUpload" @change="($event) => {
                    targetFileUrl = $event
                }" class="max-h-96 w-full"></media-upload>
            <button
                class="self-end rounded-md bg-indigo-600 px-3 py-1 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
                @click="addTargetFile">Add</button>
        </div>
        <ul v-show="show" class="grid grid-cols-2 md:grid-cols-6 gap-5 p-2">
            <li v-for="(file, index) in filteredTargets" :key="index"
                class="flex flex-col relative rounded-md  hover:shadow-cyan-300 shadow-xl" :class="{
                    'outline outline-4 outline-cyan-400 shadow-cyan-300': isSelected(file)
                }" @click.prevent="toggleSelection(file)">
                <div class="flex flex-col">
                    <video v-if="file.url.endsWith('.mp4')" :src="file.url" controls
                        class="bg-black rounded-t-md h-52 w-full">
                    </video>
                    <img v-if="file.url.endsWith('.png') || file.url.endsWith('.jpg')" :src="file.url"
                        class="rounded-t-md h-52 w-full object-cover" />
                </div>


                <div class="flex items-center justify-between px-1 py-2">
                    <span class="text-sm text-black font-semibold truncate">
                        {{ file.name }}
                    </span>
                    <div class="flex items-center justify-between gap-2">
                        <span class="select-none text-lg md:text-sm  cursor-pointer"
                            @click.stop="toggleFullscreen(file)">☐</span>
                        <span class="select-none text-lg md:text-sm  cursor-pointer"
                            @click.stop="deleteFile(file.name)">&#128465;</span>
                    </div>
                </div>
            </li>
        </ul>
        <full-screen-media v-if="isFullScreen" :mediaSrc="fullScreenMediaFile" :list="filteredTargets" />
    </div>
</template>
<script setup>
import { onMounted, ref, computed, watch } from 'vue';
import axios from 'axios';
import MediaTypeSelect from './MediaTypeSelect.vue';
import FullScreenMedia from './FullScreenMedia.vue';
import MediaUpload from './MediaUpload.vue';
import { useNormalizeUrl } from './hooks/useNormalizeUrl';

const props = defineProps({
    source: {
        type: [Object, undefined],
        default: undefined,
    },
    outputs: {
        type: Array,
        default: () => ([]),
    }
})

const server = ref(sessionStorage.getItem('server', ''));
const key = ref(sessionStorage.getItem('key') || '');

const show = ref(false);

onMounted(() => {
    fetchMediaFiles();
});

watch(() => props.source, () => {
    selected.value = [];
})

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

const mediaFiles = ref([]);
const fetchMediaFiles = async () => {
    try {
        const response = await axios(`${useNormalizeUrl(server.value)}/list-target`, {
            headers: {
                Authorization: `Bearer ${key.value}`
            }
        });

        const data = response.data?.data || [];
        mediaFiles.value = data.sort((a, b) => b.name.split('.')[0] - a.name.split('.')[0]);
    } catch (error) {
        console.error('There was an error!', error);
    }
};

const mediaType = ref(null);
const filteredTargets = computed(() => {
    let filtered = mediaFiles.value;
    if (props.source) {
        filtered = filtered.filter((f) => {
            let sourceName = props.source.name.split('.')[0];
            let targetName = f.name.split('.')[0];
            return !props.outputs.find((o) => {
                return o.name.indexOf(`${sourceName}_${targetName}`) !== -1;
            })
        })
    }

    if (mediaType.value) {
        filtered = filtered.filter((f) => {
            if (mediaType.value === 'image') {
                return f.name.endsWith(`.png`) || f.name.endsWith(`.jpg`);
            } else if (mediaType.value === 'video') {
                return f.name.endsWith(`.mp4`);
            }
        });
    }

    return filtered
})
const mediaUpload = ref();
const targetFileUrl = ref();
const addTargetFile = async () => {
    if (!targetFileUrl.value) {
        alert('Please provide url for source image!')
    }

    try {
        const response = await axios.post(`${useNormalizeUrl(server.value)}/download_target`, targetFileUrl.value, {
            headers: {
                'Content-Type': 'multipart/form-data',
                'Authorization': `Bearer ${key.value}`,
            }
        });
        console.log('Upload successful:', response.data);

        targetFileUrl.value = undefined;
        mediaFiles.value.unshift(response.data);

        mediaUpload.value.mediaSrc = undefined;
        mediaUpload.value.mediaType = undefined;
    } catch (error) {
        console.error('There was an error!', error);
    }
}

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
                dir: 'target'
            }
        });

        mediaFiles.value = mediaFiles.value.filter((mf) => mf.name !== fileName);
    } catch (error) {
        console.error('There was an error!', error);
    }
}

const selected = ref([]);

const isSelected = (file) => {
    return !!selected.value.find((sf) => sf.name === file.name)
}

const toggleSelection = (file) => {
    if (isSelected(file)) {
        selected.value = selected.value.filter((sf) => sf.name !== file.name);
    } else {
        selected.value.push(file);
    }
}

const faceEnhancer = ref(false);
const defaultArgs = '--face-selector-mode many --face-analyser-order top-bottom';
const commandArgs = ref(defaultArgs);

watch(() => faceEnhancer.value, (newVal) => {
    if (newVal) {
        commandArgs.value = `--frame-processors face_swapper face_enhancer ${defaultArgs} `
    } else {
        commandArgs.value = `--frame-processors face_swapper ${defaultArgs}`
    }
}, { immediate: true })

defineExpose({
    selected,
    mediaFiles,
    commandArgs
})
</script>