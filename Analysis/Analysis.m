%% TODO
% Find the epochs
% Remove the attack and decay period of each (5ms and 5ms)

%% Setup
participant = 3;
[stimuli, fs] = audioread("FluteStimuli_208Hz_178ms.wav");
[ref, fs] = audioread([num2str(participant), '_FFR_Stimuli.wav']);
[ffr, fs] = audioread([num2str(participant), '_FFR_Data.wav']);

gap = 0.025 * fs;
time_overlap = 0.5 * length(stimuli);
repetitions = 12000;

%% Plotting reps

plot(ref(1:fs,1));

figure
plot(stimuli);

figure
plot(stimuli(1:467,1))

figure 
stimuli_attack = stimuli(1:467,1);

%% Find the timings of the epochs
epoch_start_index = zeros(repetitions, 1);

start_index = 1;
end_index = start_index + (length(stimuli) + gap + time_overlap) + 1;

for i = 1:repetitions
    if start_index >= length(ref)
        warning('Reached the end of ref. Stopping loop.');
        break;
    end
    
    end_index = min(end_index, length(ref));
    [corr_values, lags] = xcorr(ref(start_index:end_index), stimuli);
    [~, max_index] = max(corr_values);
    best_lag = abs(lags(max_index));
    
    start_index = start_index + best_lag + length(stimuli) + gap;
    end_index = start_index + (length(stimuli) + gap + time_overlap) + 1;
    epoch_start_index(i) = start_index;
end


%% Epoch finding validation
% Number of samples to plot
plot_length = fs*5;

% Plot the reference signal
plot(ref(1:plot_length, 1));
hold on;  % Hold on to overlay another plot

% Loop through each start index in epoch_start_index
for i = 1:length(epoch_start_index)
    % Current start index
    start_idx = onset_indicies(i);
    
    % Check if the stimuli_attack can fit in the plot from the start index
    if start_idx + length(stimuli) - 1 <= plot_length
        % Overlay stimuli_attack at the correct start index
        plot(start_idx:(start_idx + length(stimuli) - 1), stimuli, 'r');
    else
        % Calculate the number of points that can fit
        num_fit_points = plot_length - start_idx + 1;
        if num_fit_points > 0  % Ensure there's space to plot something
            plot(start_idx:(start_idx + num_fit_points - 1), stimuli(1:num_fit_points), 'r');
        end
    end
end

hold off;  % Release the hold to stop overlaying plots


%% Plotting time differences
differences = diff(epoch_start_index);
disp(median(differences))
gaps = differences - length(stimuli);
disp(median(gaps/fs))

%% Verify first intex
plot(ref(start_index:start_index + length(stimuli) + gap))
hold on
plot(stimuli)

