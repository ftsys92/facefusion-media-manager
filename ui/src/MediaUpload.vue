<template>
  <div class="
        relative
        flex flex-col
        justify-center
        items-center
        bg-gray-50
        border-4 border-dashed border-gray-300
        rounded-lg
        min-h-32
        max-h-52
        hover:border-blue-500
        transition-all
        duration-300
        ease-in-out
        cursor-pointer
        select-none
        box-content
        p-2
      " @click.stop="handleMainAreaClick" @contextmenu.prevent="handleMainAreaClick" @dragover.prevent
    @drop="handleDrop" tabindex="0" ref="mainAreaRef" @mouseenter="() => isFocused = true"
    @mouseleave="() => isFocused = false" @focus="isFocused = true" @blur="isFocused = false">
    <!-- Hidden inputs for uploading images -->
    <input type="file" ref="fileInput" @change="handleFileChange" class="hidden"
      accept="image/jpeg,image/png,video/mp4" />
    <!-- Hidden text input for handling paste for images as base64 or URLs -->
    <input type="text" ref="hiddenTextInput" class="hidden" @input="handleHiddenTextInput" />

    <!-- Display area for the image or default content -->
    <div v-if="mediaSrc" class="relative w-auto min-h-[inherit] max-h-[inherit] flex-shrink">
      <video v-if="mediaType === 'video/mp4' || mediaSrc.endsWith('.mp4')" :src="mediaSrc" controls
        class="bg-black w-auto min-h-[inherit] max-h-[inherit] flex-shrink object-contain rounded-lg shadow-md">
      </video>
      <img v-else :src="mediaSrc"
        class="w-auto min-h-[inherit] max-h-[inherit] flex-shrink object-contain rounded-lg shadow-md"
        alt="Uploaded Image" />
      <button @click.stop="clearImage"
        class="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center bg-red-600 hover:bg-red-700 text-white font-bold text-sm rounded-full transition-colors duration-200">
        <span class="w-full h-full">x</span>
      </button>
    </div>
    <template v-else>
      <div class="text-center p-10">
        <p class="text-gray-700 font-semibold text-lg">
          Drop an image here or click to upload
        </p>
        <p v-if="!detectMob()" class="text-gray-500 text-sm mt-2">(Or right-click for options)</p>
      </div>
    </template>

    <!-- Custom context menu -->
    <div v-show="showContextMenu" class="absolute z-10 w-48 bg-white rounded-md shadow-lg" ref="contextMenuRef"
      :style="{ top: `${menuPosition.y}px`, left: `${menuPosition.x}px` }">
      <ul class="text-gray-700">
        <li class="px-4 py-2 hover:bg-gray-100 cursor-pointer" @click.stop="triggerFileUpload">
          Upload Image
        </li>
        <li class="px-4 py-2 hover:bg-gray-100 cursor-pointer" @click.stop="triggerClipboardModal">
          Paste
        </li>
        <li class="px-4 py-2 hover:bg-gray-100 cursor-pointer" :class="{ 'opacity-50 cursor-not-allowed': !mediaSrc }"
          @click.stop="mediaSrc ? clearImage() : null">
          Clear
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue';
function detectMob() {
  const toMatch = [
    /Android/i,
    /webOS/i,
    /iPhone/i,
    /iPad/i,
    /iPod/i,
    /BlackBerry/i,
    /Windows Phone/i
  ];
  return toMatch.some((toMatchItem) => {
    return navigator.userAgent.match(toMatchItem);
  });
}

const emit = defineEmits(['change'])

const mediaSrc = ref();
const mediaType = ref();
const showContextMenu = ref(false);
const menuPosition = reactive({ x: 0, y: 0 });
const fileInput = ref(null);
const hiddenTextInput = ref(null);


async function convertToBlob(data) {
  if (data.startsWith('blob:')) {
    // It's already a blob URL, fetch the blob
    const response = await fetch(data);
    return response.blob();
  } else if (data.startsWith('data:')) {
    // Convert base64 to blob
    const response = await fetch(data);
    return response.blob();
  } else if (data.startsWith('http')) {
    // For URLs, fetch the content and return as blob
    const response = await fetch(data);
    return response.blob();
  } else {
    // If it's neither, it might be an error
    throw new Error('Unsupported media type or data');
  }
}

watch(() => ({ src: mediaSrc.value, type: mediaType.value }), async (newVal) => {
  if (!newVal.src) {
    emit('change', undefined); // Emitting undefined when there's no media
    return;
  }

  try {
    // Convert all media types to Blob
    const blob = await convertToBlob(newVal.src);

    // Then, convert Blob to File if necessary
    const fileName = newVal.type.startsWith('video/') ? 'video.mp4' : newVal.type.startsWith('image/jpeg') ? 'image.jpg' : 'image.png'; // You can be more specific with names
    const mediaFile = new File([blob], fileName, { type: blob.type });

    // Construct FormData to send to the backend
    const formData = new FormData();
    formData.append('media', mediaFile);

    console.log({ formData, type: blob.type })
    emit('change', formData); // Emit FormData and type for backend processing
  } catch (error) {
    console.error('Error processing media for upload:', error);
    emit('change', undefined); // In case of error, emit undefined or some error state
  }
}, { deep: true });


const handleMainAreaClick = (event) => {
  if (showContextMenu.value) {
    showContextMenu.value = false
    return
  }

  if (detectMob() || event?.button === 2) {
    openContextMenu(event)
  } else if (event.button === 0) {
    triggerFileUpload();
  }
};

const contextMenuRef = ref(null);
const mainAreaRef = ref(null);

const openContextMenu = async (event) => {
  // Prevent default to avoid focusing any hidden input
  event.preventDefault()
  menuPosition.x = event.layerX;
  menuPosition.y = event.layerY;
  showContextMenu.value = true;

  await nextTick();

  if (contextMenuRef.value) {
    const menuWidth = contextMenuRef.value.clientWidth;
    const menuHeight = contextMenuRef.value.clientHeight;
    const viewportWidth = mainAreaRef.value.clientWidth;
    const viewportHeight = mainAreaRef.value.clientHeight;

    // Adjust position if the context menu would go off the right side of the screen
    if (event.layerX + menuWidth > viewportWidth) {
      menuPosition.x = Math.abs(event.layerX - menuWidth);
    } else {
      menuPosition.x = event.layerX;
    }

    // Adjust position if the context menu would go off the bottom of the screen
    if (event.layerY + menuHeight > viewportHeight) {
      menuPosition.y = Math.abs(event.layerY - menuHeight);
    } else {
      menuPosition.y = event.layerY;
    }
  }
};

const closeContextMenu = () => {
  showContextMenu.value = false;
};

const triggerFileUpload = () => {
  fileInput.value?.click();
  closeContextMenu();
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file && file.type.startsWith('image/') || file.type.startsWith('video/')) {
    mediaSrc.value = URL.createObjectURL(file);
    mediaType.value = file.type;
  }
};

const handleDrop = (event) => {
  event.preventDefault();
  const files = event.dataTransfer.files;
  if (files.length > 0) {
    const file = files[0];
    if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
      mediaSrc.value = URL.createObjectURL(file);
      mediaType.value = file.type;
    }
  }
  closeContextMenu();
};

async function getClipboardContents() {
  try {
    const text = await navigator.clipboard.readText(); // Try to read as text first

    if (text.startsWith('data:image') || text.startsWith('http')) {
      // We have a base64 image string
      mediaSrc.value = text;
      mediaType.value = text.startsWith('data:image') ? 'base64' : 'url';
    } else {
      // Not a base64 string, check for blob data
      const clipboardItems = await navigator.clipboard.read();
      console.log(clipboardItems)
      for (const clipboardItem of clipboardItems) {
        for (const type of clipboardItem.types) {
          if (type.startsWith('image/') || type.startsWith('video/')) {
            // We have an image blob
            const blob = await clipboardItem.getType(type);
            mediaSrc.value = URL.createObjectURL(blob);
            mediaType.value = type;
            return; // Exit after processing the first item
          }
        }
      }
    }
  } catch (err) {
    console.error('Failed to read clipboard contents:', err.name, err.message);
  }
}

// Paste handling
const isFocused = ref(false);
const handlePaste = async (event) => {
  if (!isFocused.value) return; // Only proceed if this component is focused

  const items = event.clipboardData?.items;
  for (const item of items) {
    if (item.type.startsWith('image') || item.type.startsWith('video')) {
      const blob = item.getAsFile();
      mediaSrc.value = URL.createObjectURL(blob);
      mediaType.value = item.type;
    } else if (item.kind === 'string') {
      item.getAsString((s) => {
        if (s.startsWith('data:image') || s.startsWith('http')) {
          mediaSrc.value = s;
          mediaType.value = s.startsWith('data:image') ? 'base64' : 'url';
        }
      })
    }
  }
  closeContextMenu();
};


// Function triggered by the custom context menu to handle paste operations
const triggerClipboardModal = async (event) => {
  document.documentElement.focus(); // Focus on the hidden input
  await nextTick()
  await getClipboardContents(); // Attempt to retrieve and display the clipboard contents
  closeContextMenu(); // Close the context menu
};

const handleHiddenTextInput = (event) => {
  // This will be called when the hidden input detects an input event, which can be from a paste action
  event.stopPropagation()
  closeContextMenu(); // Close context menu if open
};

const clearImage = () => {
  mediaSrc.value = null;
  fileInput.value.value = null
  closeContextMenu();
};

const globalClickListener = () => {
  if (showContextMenu.value) {
    showContextMenu.value = false;
  }
};

onMounted(() => {
  window.addEventListener('click', globalClickListener);
  document.addEventListener('paste', handlePaste)
});

onUnmounted(() => {
  window.removeEventListener('click', globalClickListener);
  document.removeEventListener('paste', handlePaste)
});

defineExpose({
  mediaSrc,
  mediaType,
})
</script>
