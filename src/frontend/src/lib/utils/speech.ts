/**
 * Browser-based Text-to-Speech using Web Speech API
 */

let speechSynthesis: SpeechSynthesis | null = null;
let lastSpokenTime: { [key: string]: number } = {};

export function initSpeech() {
	if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
		speechSynthesis = window.speechSynthesis;
		console.log('[Speech] Web Speech API available');
		return true;
	}
	console.warn('[Speech] Web Speech API not available');
	return false;
}

export function speak(text: string, priority: 'high' | 'normal' | 'low' = 'normal') {
	if (!speechSynthesis) {
		initSpeech();
	}
	
	if (!speechSynthesis) {
		console.warn('[Speech] Cannot speak, API not available');
		return;
	}
	
	// Rate limiting based on priority
	const now = Date.now();
	const intervals = {
		high: 800,
		normal: 1800,
		low: 3500
	};
	
	const lastTime = lastSpokenTime[text] || 0;
	if (now - lastTime < intervals[priority]) {
		console.log('[Speech] Skipping (too soon):', text);
		return;
	}
	
	// Cancel any ongoing speech
	speechSynthesis.cancel();
	
	// Create utterance
	const utterance = new SpeechSynthesisUtterance(text);
	utterance.rate = 1.0;
	utterance.pitch = 1.0;
	utterance.volume = 1.0;
	utterance.lang = 'en-US';
	
	// Speak
	speechSynthesis.speak(utterance);
	lastSpokenTime[text] = now;
	
	console.log('[Speech] Speaking:', text);
}

export function stopSpeech() {
	if (speechSynthesis) {
		speechSynthesis.cancel();
	}
}

