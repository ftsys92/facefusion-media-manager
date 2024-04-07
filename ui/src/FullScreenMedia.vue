<template>
    <div v-if="props.mediaSrc" tabindex="0" class="flex flex-col items-stretch relative" ref="wrapper"
        @keydown.space="doSwipeRight">
        <PinchScrollZoom v-if="current.endsWith('.png') || current.endsWith('.jpg')" centered key-actions
            :within="false" :width="windowWidth" :height="windowHeight">
            <img :src="current" class="rounded-md w-full h-full object-contain rotate" draggable="false" :class="{
        [rotateClasses[currentRotateIndex]]: true
    }" />
        </PinchScrollZoom>

        <video v-if="current.endsWith('.mp4')" :src="current" controls class="rounded-md h-full w-full">
        </video>
        <span
            class="pointer-events-auto text-[2.25rem] text-green-400 opacity-[0.3] hover:opacity-100 cursor-pointer absolute top-0 right-3 mr-2"
            @click.prevent="exitFullscreen">&times;</span>
        <span
            class="pointer-events-auto text-[2.25rem] text-green-400 opacity-[0.3] hover:opacity-100 cursor-pointer absolute bottom-10 right-3 mr-2"
            @click.prevent="exitFullscreen">&times;</span>
        <span
            class="pointer-events-auto text-[2.25rem] text-green-400 opacity-[0.3] hover:opacity-100 cursor-pointer absolute bottom-10 right-24 mr-2"
            @click.prevent="playPause">{{ slideShowRunning ? '&#10073;&#10073;' : '&#9658;' }}</span>
        <span
            class="pointer-events-auto text-[2.25rem] text-green-400 opacity-[0.3] hover:opacity-100 cursor-pointer absolute bottom-10 right-12 mr-2"
            @click.prevent="rotate">↻</span>
        <span
            class="pointer-events-auto text-[2.25rem] text-green-400 opacity-[0.3] hover:opacity-100 cursor-pointer absolute top-[45%] ml-2"
            @click.prevent="doSwipeLeft">&larr;</span>
        <span
            class="pointer-events-auto text-[2.25rem] text-green-400 opacity-[0.3] hover:opacity-100 cursor-pointer absolute top-[45%] right-0 mr-2"
            @click.prevent="doSwipeRight">&rarr;</span>
    </div>
</template>
<script setup>
import PinchScrollZoom from '@coddicat/vue-pinch-scroll-zoom';
import { nextTick, onMounted, ref } from 'vue';

const props = defineProps({
    mediaSrc: {
        type: String,
        required: true,
    },
    list: {
        type: Array,
        required: true,
    }
});

const current = ref(props.mediaSrc);

const doSwipeLeft = () => {
    const index = props.list.findIndex((e) => e.url === current.value)
    current.value = props.list[index > 0 ? index - 1 : props.list.length - 1].url

}

const doSwipeRight = () => {
    const index = props.list.findIndex((e) => e.url === current.value)
    current.value = props.list[index < props.list.length - 1 ? index + 1 : 0].url
}

const windowWidth = ref(window?.innerWidth);
const windowHeight = ref(window?.innerHeight);
window.addEventListener('resize', () => {
    windowWidth.value = window?.innerWidth
    windowHeight.value = window?.innerHeight
});

const wrapper = ref();
onMounted(() => {
    wrapper.value.requestFullscreen().then(() => {
        nextTick().then(() => {
            wrapper.value.focus();
        })
    });
})

const exitFullscreen = () => {
    slideShowRunning.value = false;
    clearInterval(slideShowInterval.value);
    if (document.fullscreenElement) {
        document.exitFullscreen();
    }
}

const rotateClasses = ref([
    'rotate-0',
    'rotate-90',
    'rotate-180',
    '-rotate-90',
]);

const currentRotateIndex = ref(0)
const rotate = () => {
    currentRotateIndex.value = currentRotateIndex.value >= rotateClasses.value.length - 1 ? 0 : currentRotateIndex.value + 1
    console.log(currentRotateIndex.value)
}

const slideShowRunning = ref(false);
const slideShowInterval = ref();
const playPause = () => {
    if (slideShowRunning.value) {
        slideShowRunning.value = false;
        clearInterval(slideShowInterval.value);
        return;
    }
    slideShowRunning.value = true;
    slideShowInterval.value = setInterval(() => {
        doSwipeRight();
    }, 8000);
}
</script>