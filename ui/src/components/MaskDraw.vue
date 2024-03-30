<template>
    <div tabindex="0" class="flex flex-col items-stretch relative gap-2 text-xs rounded-md select-none p-4"
        ref="wrapper">
        <div class="flex items-center justify-between bg-white p-2 shadow-lg rounded-md">
            <div class="flex flex-col items-start gap-2">
                <input type="color" v-model="brushColor" class="form-control">
                <input type="range" v-model="brushSize" min="1" max="50" class="range range-primary">
            </div>
            <div class="grid grid-cols-2 gap-2">
                <button @click="saveImage"
                    class="text-xs py-0.5 px-2 bg-violet-700 text-white border border-violet-400 rounded-lg shadow-md disabled:opacity-50">Save</button>
                <button @click="close"
                    class="text-xs py-0.5 px-2 bg-violet-700 text-white border border-violet-400 rounded-lg shadow-md disabled:opacity-50">Close</button>
                <button @click="toggleDrawing"
                    class="text-xs py-0.5 px-2 bg-violet-700 text-white border border-violet-400 rounded-lg shadow-md disabled:opacity-50">{{
                    isDrawing ? 'Move' : 'Draw' }}</button>
                <button @click="reset"
                    class="text-xs py-0.5 px-2 bg-violet-700 text-white border border-violet-400 rounded-lg shadow-md disabled:opacity-50">Reset</button>

            </div>
        </div>

        <PinchScrollZoom v-if="windowWidth && windowHeight" ref="zoomer" centered :draggable="!isDrawing" :within="true"
            class="rounded-md overflow-hidden w-full h-full bg-black">
            <div class="relative">
                <canvas :width="canvasWidth" :height="canvasHeight" class="rounded-md absolute top-0 left-0"
                    ref="canvasRef" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing"
                    @mouseleave="stopDrawing" @touchstart.prevent="startDrawing" @touchmove.prevent="draw"
                    @touchend.prevent="stopDrawing">
                </canvas>
                <img :src="props.image.url" ref="imageRef" class="rounded-md w-full h-full object-contain rotate"
                    draggable="false" />
            </div>
        </PinchScrollZoom>
    </div>
</template>
<script setup>
import PinchScrollZoom from '@coddicat/vue-pinch-scroll-zoom';
import { nextTick, onMounted, ref, reactive } from 'vue';

const props = defineProps({
    image: {
        type: Object,
        required: true,
    }
});

const emit = defineEmits(['mask', 'close']);

const canvasRef = ref(null);
const imageRef = ref(null);
const isDrawing = ref(false);
const drawingState = reactive({
    isDrawing: false,
    lastX: 0,
    lastY: 0
});

const windowWidth = ref(0);
const windowHeight = ref(0);
const canvasWidth = ref(0);
const canvasHeight = ref(0);

const updateCanvasSize = () => {
    nextTick(() => {
        if (imageRef.value) {
            canvasWidth.value = imageRef.value.width;
            canvasHeight.value = imageRef.value.height;
        }
    });
};

window.addEventListener('resize', updateCanvasSize);

const wrapper = ref();
onMounted(() => {
    windowWidth.value = wrapper.value.offsetWidth
    windowHeight.value = wrapper.value.offsetHeight
    updateCanvasSize();
    nextTick(() => {
        reset();
    })

});

const getCoordinates = (event) => {
    const rect = canvasRef.value.getBoundingClientRect(); // This always gets the current position and size
    if (event.touches && event.touches.length > 0) {
        return {
            x: (event.touches[0].clientX - rect.left) / (rect.width / canvasWidth.value), // Adjust based on actual size vs displayed size
            y: (event.touches[0].clientY - rect.top) / (rect.height / canvasHeight.value)
        };
    } else {
        return {
            x: (event.clientX - rect.left) / (rect.width / canvasWidth.value),
            y: (event.clientY - rect.top) / (rect.height / canvasHeight.value)
        };
    }
};

const startDrawing = (event) => {
    if (!isDrawing.value) return;
    const { x, y } = getCoordinates(event);
    drawingState.isDrawing = true;
    [drawingState.lastX, drawingState.lastY] = [x, y];
};

const brushSize = ref(5);
const brushColor = ref('#a78bfa')
const draw = (event) => {
    if (!drawingState.isDrawing) return;
    const { x, y } = getCoordinates(event);

    const ctx = canvasRef.value.getContext('2d');
    ctx.strokeStyle = brushColor.value;
    ctx.lineWidth = brushSize.value;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(drawingState.lastX, drawingState.lastY);
    ctx.lineTo(x, y);
    ctx.stroke();
    [drawingState.lastX, drawingState.lastY] = [x, y];
};

const clearCanvas = () => {
    const ctx = canvasRef.value.getContext('2d');
    ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);
}

const stopDrawing = () => {
    drawingState.isDrawing = false;
};

const toggleDrawing = () => {
    isDrawing.value = !isDrawing.value;
};

const zoomer = ref();
const reset = () => {
    zoomer.value?.setData({
        scale: 1,
        originX: 0,
        originY: 0,
        translateX: 0,
        translateY: 0
    });
    clearCanvas()
}

const close = () => {
    emit('close')
}

const saveImage = async () => {
    // Create a temporary canvas
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');

    // Use natural dimensions of the image for the canvas size
    const naturalWidth = imageRef.value.naturalWidth;
    const naturalHeight = imageRef.value.naturalHeight;
    tempCanvas.width = naturalWidth;
    tempCanvas.height = naturalHeight;

    // Scale the drawing context to match the natural size of the image
    const scaleX = naturalWidth / canvasRef.value.width;
    const scaleY = naturalHeight / canvasRef.value.height;
    tempCtx.scale(scaleX, scaleY);

    // Draw the original canvas content onto the temporary canvas
    tempCtx.drawImage(canvasRef.value, 0, 0, canvasRef.value.width, canvasRef.value.height);

    // ImageData to manipulate pixels
    let imgData = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
    let data = imgData.data; // the array of RGBA values

    // Loop through all pixels - invert colors
    for (let i = 0; i < data.length; i += 4) {
        // Change non-white pixels to white, and white to black
        // Assuming white is the predominant color for lines
        if (data[i] > 200 && data[i + 1] > 200 && data[i + 2] > 200) { // if white or light-colored
            data[i] = 0;     // set red to 0
            data[i + 1] = 0; // set green to 0
            data[i + 2] = 0; // set blue to 0
        } else { // for darker colors, change to white
            data[i] = 255;     // set red to 255
            data[i + 1] = 255; // set green to 255
            data[i + 2] = 255; // set blue to 255
        }
    }

    // Update the canvas with the inverted colors
    tempCtx.putImageData(imgData, 0, 0);

    // Fill the background with black (where it was white originally)
    tempCtx.globalCompositeOperation = 'destination-over';
    tempCtx.fillStyle = 'black';
    tempCtx.fillRect(0, 0, canvasRef.value.width, canvasRef.value.height);

    // Convert the temporary canvas to a data URL and output it
    const mask = tempCanvas.toDataURL("image/png");

    emit('mask', {
        image: await convertImageToBase64(props.image.url),
        mask,
        w: naturalWidth,
        h: naturalHeight
    });

    // Clean up: remove the temporary canvas if not needed anymore
    tempCanvas.remove();
};

async function convertImageToBase64(imageUrl) {
    try {
        const response = await fetch(imageUrl); // Ensure CORS mode is set
        const blob = await response.blob();

        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result); // This is the Base64 string
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    } catch (error) {
        console.error('Error converting image to Base64:', error);
        return '';
    }
}





</script>