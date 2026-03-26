import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useOllamaStore = defineStore('ollama', () => {
    const isInstalled = ref(true);
    const isConnected = ref(false);
    const models = ref<any[]>([]);
    const recommendation = ref<any>(null);
    const isInstalling = ref(false);
    const installProgress = ref({ status: 'idle', percent: 0, message: '' });
    const pullProgress = ref<Record<string, { status: string, percent: number }>>({});

    let pollInterval: number | null = null;

    async function fetchHealth() {
        try {
            const res = await fetch('/api/health');
            if (res.ok) {
                const data = await res.json();
                isInstalled.value = data.ollama_installed;
                isConnected.value = data.ollama_connected;
            }
        } catch (e) {
            console.error('Failed to fetch health', e);
            isConnected.value = false;
        }
    }

    function startPolling(intervalMs = 30000) {
        if (pollInterval) return;
        fetchHealth();
        pollInterval = window.setInterval(fetchHealth, intervalMs);
    }

    function stopPolling() {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }

    async function fetchModels() {
        // ... (existing code)
        try {
            const res = await fetch('/api/models');
            if (res.ok) {
                const data = await res.json();
                models.value = data.models;
            }

            const recRes = await fetch('/api/models/recommend');
            if (recRes.ok) {
                recommendation.value = await recRes.json();
            }
        } catch (e) {
            console.error('Failed to fetch models', e);
        }
    }

    async function installOllama() {
        if (isInstalling.value) return;
        isInstalling.value = true;
        installProgress.value = { status: 'starting', percent: 0, message: 'Starting installation...' };

        try {
            const response = await fetch('/api/ollama/install', { method: 'POST', body: JSON.stringify({ accept_terms: true }), headers: { 'Content-Type': 'application/json' } });
            const reader = response.body?.getReader();
            if (!reader) throw new Error('ReadableStream not supported');

            const decoder = new TextDecoder();
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        installProgress.value = data;
                        if (data.status === 'success') {
                            isInstalled.value = true;
                            await fetchHealth();
                        }
                    } catch (e) {
                        console.error('Failed to parse install chunk', e);
                    }
                }
            }
        } catch (e: any) {
            installProgress.value = { status: 'error', percent: 0, message: e.message || 'Installation failed' };
        } finally {
            isInstalling.value = false;
        }
    }

    async function pullModel(name: string) {
        pullProgress.value[name] = { status: 'starting', percent: 0 };
        try {
            const res = await fetch('/api/models/pull', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name }),
            });

            const reader = res.body?.getReader();
            if (!reader) throw new Error('Stream not supported');

            const decoder = new TextDecoder();
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        const percent = data.total ? (data.completed / data.total) * 100 : 0;
                        pullProgress.value[name] = {
                            status: data.status,
                            percent: Math.round(percent)
                        };
                        if (data.status === 'success') {
                            await fetchModels();
                        }
                    } catch (e) {
                        // ignore partial lines
                    }
                }
            }
        } catch (e) {
            console.error('Failed to pull model', e);
            pullProgress.value[name] = { status: 'error', percent: 0 };
        }
    }

    return {
        isInstalled,
        isConnected,
        models,
        recommendation,
        isInstalling,
        installProgress,
        pullProgress,
        fetchHealth,
        fetchModels,
        installOllama,
        pullModel,
        startPolling,
        stopPolling
    };
});
