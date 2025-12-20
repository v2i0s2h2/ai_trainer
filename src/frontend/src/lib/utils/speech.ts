/**
 * Browser-based Text-to-Speech using Web Speech API
 */

// Store loaded voices
let voices: SpeechSynthesisVoice[] = [];
let lastSpokenTime: Record<string, number> = {};

function loadVoices() {
	if (typeof window !== 'undefined' && window.speechSynthesis) {
		voices = window.speechSynthesis.getVoices();
		console.log('[Speech] Loaded voices:', voices.length);
	}
}

export function initSpeech() {
	if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
		console.log('[Speech] Web Speech API available');

		// Load voices initially
		loadVoices();

		// Handle async voice loading (Chrome/Brave requires this)
		if (window.speechSynthesis.onvoiceschanged !== undefined) {
			window.speechSynthesis.onvoiceschanged = loadVoices;
		}

		return true;
	}
	console.warn('[Speech] Web Speech API not available');
	return false;
}

export function speak(text: string, priority: 'high' | 'normal' | 'low' = 'normal') {
	if (typeof window === 'undefined' || !window.speechSynthesis) {
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
	window.speechSynthesis.cancel();

	// Create utterance
	const utterance = new SpeechSynthesisUtterance(text);
	utterance.rate = 1.0;
	utterance.pitch = 1.0;
	utterance.volume = 1.0;
	utterance.lang = 'en-US';

	// Explicitly select voice for Linux compatibility
	if (voices.length === 0) {
		loadVoices();
	}

	if (voices.length > 0) {
		// Prefer Google US English, then any English, then default
		const voice = voices.find(v => v.name.includes('Google') && v.lang.includes('en-US'))
			|| voices.find(v => v.lang.includes('en') || v.lang.includes('US'))
			|| voices[0];

		if (voice) {
			utterance.voice = voice;
		}
	}

	// Speak
	window.speechSynthesis.speak(utterance);
	lastSpokenTime[text] = now;

	console.log('[Speech] Speaking:', text);
}

export function stopSpeech() {
	if (typeof window !== 'undefined' && window.speechSynthesis) {
		window.speechSynthesis.cancel();
	}
}

