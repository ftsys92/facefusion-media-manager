<template>
    <select v-model="type">
        <option :value="null">All</option>
        <option value="image">Image</option>
        <option value="video">Video</option>
    </select>
</template>
<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
    modelValue: {
        type: [String, null],
        default: null,
    }
});

const emit = defineEmits(['update:modelValue']);

const type = ref(props.modelValue);
watch(() => type.value, (newVal) => {
    emit('update:modelValue', newVal)
});
</script>