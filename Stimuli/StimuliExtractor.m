[y,fs] = audioread("Flute208Hz.wav");

signal_Duration = 175 * fs / 1000;

start_Point = 64191; %arbitrary chosen as a zero crossing point in the sustained portion
stimuli = y(start_Point:start_Point + signal_Duration - 1, 1);

AD = linspace(0, 1, 5 * fs/1000)'; % 5Ms for attack and decay part 
envelope = ones(length(stimuli) - (2*length(AD)), 1);
envelope = [AD; envelope; flip(AD)];
stimuli = envelope .* stimuli; 

audiowrite("FluteStimuli.wav",stimuli,fs);