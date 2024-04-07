<template>
    <div class="w-full p-2">
        <div class="flex flex-col items-start justify-between gap-2">
            <h2 class="text-lg font-bold mb-2 cursor-pointer" @click="show = !show">
                <span class="text-xs">{{ show ? '&#9660;' : '&#9650;' }}</span> Sources <span class="text-xs">{{
                selected && 1 || 0 }}</span>
            </h2>
        </div>
        <div v-show="show" class="flex flex-col items-center gap-2 w-full p-1">
            <media-upload ref="mediaUpload" @change="($event) => {
                sourceFileUrl = $event
            }" class="max-h-96 w-full"></media-upload>
            <button
                class="self-end rounded-md bg-indigo-600 px-3 py-1 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
                @click="addSourceFile">Add</button>
        </div>
        <ul v-show="show" class="grid grid-cols-3 md:grid-cols-6 gap-5 p-2">
            <li v-for="(file, index) in mediaFiles" :key="index"
                class="flex flex-col relative rounded-md hover:shadow-cyan-300 shadow-xl" :class="{
                'outline outline-4 outline-cyan-400': isSelected(file)
            }" @click.prevent="toggleSelection(file)">
                <div class="flex flex-col">
                    <video v-if="file.url.endsWith('.mp4')" :src="file.url" controls
                        class="bg-black rounded-t-md h-52 sm:h-32 w-full">
                    </video>
                    <img v-if="file.url.endsWith('.png') || file.url.endsWith('.jpg')" :src="file.url"
                        class="rounded-t-md h-52 sm:h-32 w-full object-cover" @click="() => { }" />
                </div>


                <div class="flex items-center justify-between px-1 py-2">
                    <span class="text-xs text-black font-semibold truncate">
                        {{ file.name }}
                    </span>
                    <div class="flex items-center justify-between gap-1">
                        <span class="select-none text-md md:text-sm cursor-pointer" @click.stop="inpaint(file)">☐</span>
                        <span class="select-none text-md md:text-sm cursor-pointer"
                            @click.stop="deleteFile(file.name)">&#128465;</span>
                    </div>
                </div>
            </li>
        </ul>
        <mask-draw v-if="inpaintSource" :image="inpaintSource" @close="inpaintSource = undefined" @mask="processInpaint"
            class="w-full sm:w-[500px] h-[600px]"></mask-draw>
    </div>
</template>
<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useNormalizeUrl } from './hooks/useNormalizeUrl';
import MediaUpload from './MediaUpload.vue';
import MaskDraw from './components/MaskDraw.vue';

const server = ref(sessionStorage.getItem('server', ''));
const key = ref(sessionStorage.getItem('key') || '');

const show = ref(false);

onMounted(() => {
    fetchMediaFiles();
})

const mediaFiles = ref([]);
const fetchMediaFiles = async () => {
    try {
        const response = await axios(`${useNormalizeUrl(server.value)}/list-source`, {
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

const mediaUpload = ref();
const sourceFileUrl = ref();
const addSourceFile = async () => {
    if (!sourceFileUrl.value) {
        alert('Please provide url for source image!')
    }

    try {
        const response = await axios.post(`${useNormalizeUrl(server.value)}/download_source`, sourceFileUrl.value, {
            headers: {
                'Content-Type': 'multipart/form-data',
                'Authorization': `Bearer ${key.value}`,
            }
        });
        console.log('Upload successful:', response.data);

        sourceFileUrl.value = undefined;
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
                dir: 'source'
            }
        });

        mediaFiles.value = mediaFiles.value.filter((mf) => mf.name !== fileName);
    } catch (error) {
        alert('There was an error!')
        console.error('There was an error!', error);
    }
}

const selected = ref();

const isSelected = (file) => {
    return !!(selected.value?.name === file.name)
}

const toggleSelection = (file) => {
    if (isSelected(file)) {
        selected.value = undefined;
    } else {
        selected.value = file;
    }
}

const inpaintSource = ref();
const inpaint = (file) => {
    inpaintSource.value = file;
}

const emit = defineEmits(['inpainted'])
const processInpaint = async (mask) => {
    const response = await axios.post(`${useNormalizeUrl(server.value)}/inpaint`, {
        source: inpaintSource.value.name,
        image: mask.image,
        width: mask.w,
        height: mask.h,
        mask: mask.mask,
    }, {
        headers: {
            Authorization: `Bearer ${key.value}`
        }
    });

    emit('inpainted', response?.data)
}

defineExpose({
    selected,
    mediaFiles,
})
</script>