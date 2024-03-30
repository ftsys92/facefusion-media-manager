<template>
  <div v-if="!auth" class="bg-slate-600 relative h-full p-2">
    <div class="flex flex-col items-center gap-1 max-w-60 mx-auto">
      <!--<input
        class="block w-full appearance-none bg-white px-1 text-base text-slate-900 placeholder:text-slate-600 focus:outline-none sm:text-sm sm:leading-6"
        v-model="server" placeholder="Enter server url" />-->
      <input
        type="password"
        class="block w-full appearance-none bg-white px-1 text-base text-slate-900 placeholder:text-slate-600 focus:outline-none sm:text-sm sm:leading-6"
        v-model="key" placeholder="Enter key" />
      <button
        class="pointer-events-auto ml-8 rounded-md bg-indigo-600 px-3 py-2 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
        @click="login">Login</button>
    </div>
  </div>
  <div v-else class="relative h-full">
    <div class="flex items-center justify-between bg-slate-600 p-2 sticky top-0 z-10">
      <a href="#" class="flex flex-col items-start text-xl tracking-tight font-bold  text-white">
        PHOME HUB <span class="text-xs">({{ jobs.length }} in progress)</span></a>
      <div class="flex items-center justify-between gap-2">
        <button :disabled="!source?.selected || !target?.selected?.length"
          class="rounded-md bg-indigo-600 px-3 py-2 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500 disabled:bg-gray-500 disabled:cursor-not-allowed"
          @click="proceed">Proceed</button>
        <button :disabled="!jobs.length"
          class="disabled:opacity-50 rounded-md bg-indigo-600 px-3 py-2 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500 disabled:bg-gray-500 disabled:cursor-not-allowed"
          @click="stopAll">Stop All</button>
        <button
          class="rounded-md bg-indigo-600 px-3 py-2 text-[0.8125rem] font-semibold leading-5 text-white hover:bg-indigo-500"
          @click="logout">Logout</button>
      </div>

    </div>
    <div class="flex flex-col items-start justify-between px-1 gap-5">
      <!-- SOURCES -->

      <sources ref="source" @inpainted="(event) => {
        output?.mediaFiles?.unshift(event)
      }"></sources>
      <hr class="w-full" />

      <!-- TARGETS -->
      <targets :source="source?.selected" :outputs="[...(output?.mediaFiles || []), ...jobs.map((r) => r.output_file)]"
        ref="target"></targets>
      <hr class="w-full" />

      <!-- OUTPUTS -->
      <outputs ref="output" :source="source?.selected"></outputs>
    </div>
  </div>

</template>
<script setup>
import axios from 'axios';
import { ref } from 'vue';
import Sources from './Sources.vue';
import Targets from './Targets.vue';
import Outputs from './Outputs.vue';
import { useWebsocket } from './hooks/useWebsocket';
import { useNormalizeUrl } from './hooks/useNormalizeUrl';

const auth = ref(false);
const server = ref(sessionStorage.getItem('server') || 'ff.phh.internal');
const key = ref(sessionStorage.getItem('key') || '');



const login = async () => {
  if (!server.value) {
    alert('You are not authenticated!');
    return;
  }

  try {
    const response = await axios(`${useNormalizeUrl(server.value)}/auth`, {
      headers: {
        Authorization: `Bearer ${key.value}`
      }
    });

    sessionStorage.setItem('server', server.value);
    sessionStorage.setItem('key', key.value);

    console.log(response.data.jobs)
    jobs.value.unshift(...response.data.jobs);

    auth.value = true;

    const socket = useWebsocket(useNormalizeUrl(server.value));
    socket.on('job_completed', (event) => {
      jobs.value = jobs.value.filter((j) => j.job_id !== event.job_id);
      output.value.mediaFiles.unshift(event.output_file);
    })

    socket.on('job_failed', (event) => {
      console.log(event)
      jobs.value = jobs.value.filter((j) => j.job_id !== event.job_id);
    });
  } catch (error) {
    alert('There was an error!');
    console.error('There was an error!', error);
  }
};

const logout = () => {
  auth.value = false
  server.value = '';
  key.value = '';
  sessionStorage.removeItem('server')
  sessionStorage.removeItem('key')
};

login();

const source = ref();
const target = ref();
const output = ref();

const jobs = ref([]);

const proceed = async () => {
  if (!source.value.selected?.name || !target.value.selected?.length) {
    alert('Select at least one source and target!');
    return;
  }

  const params = {
    source: source.value.selected.name,
    targets: target.value.selected.map((f) => f.name),
    other_args: target.value.commandArgs,
  }

  target.value.selected = [];

  try {
    const response = await axios(`${useNormalizeUrl(server.value)}/run-script`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${key.value}`
      },
      data: params
    });

    jobs.value.unshift(...response.data);
  } catch (error) {
    alert('There was an error!');
    console.error('There was an error!', error);
  }
}
const stopAll = async () => {
  try {
    await axios(`${useNormalizeUrl(server.value)}/stop-all`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${key.value}`
      },
    });

    jobs.value = [];
  } catch (error) {
    console.error('There was an error!', error);
  }
}

</script>