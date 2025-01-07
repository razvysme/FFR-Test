%% Setup
participant = 3;
[y_FFR, fs] = audioread([num2str(participant), '_FFR_Stimuli.wav']);
[y_Ref, fs] = audioread([num2str(participant), '_FFR_Data.wav']);

num_repetitions = 12000-1;
first_rep_onset = 4635;
onset_treshold = y_FFR(first_rep_onset);
first_index = find(y_FFR(first_rep_onset:fs) > onset_treshold, 1);

hp_cutoff = 20;
lp_cutoff = 3000;
n = 4000; 

% Design a high-pass FIR filter with the given specifications
hp_filter = fir1(n, hp_cutoff/(fs/2), 'high');
lp_filter = fir1(n, lp_cutoff/(fs/2), 'low');

y_FFR_Filtered = filter(hp_filter, 1, y_FFR); 
y_FFR_Filtered = filter(lp_filter, 1, y_FFR_Filtered); 


lp_cutoff_2 = 1000;
lp_filter_2 = fir1(n, lp_cutoff_2/(fs/2), 'low');
y_FFR_Filtered = filter(hp_filter, 1, y_FFR); 


figure(12345);
plot(y_FFR_Filtered(1:fs,1));
hold all
plot(y_FFR(1:fs,1));


y_Ref_Filtered = filter(hp_filter, 1, y_Ref); 
y_Ref_Filtered = filter(lp_filter, 1, y_Ref_Filtered); 



figure(123);
plot(y_Ref(1:fs,1));
hold all
plot(y_Ref(1:fs,1));

% Given data
signal_duration_ms = 175; % Duration of the signal in ms
gap_duration_ms = 25; % Duration of the gap in ms

% Calculate the number of samples for signal and gap
signal_samples = signal_duration_ms * fs / 1000; % 300ms in samples
gap_samples = gap_duration_ms * fs / 1000; % 50ms in samples
trial_samples = signal_samples + gap_samples; % Total samples per cycle (signal + gap)

% Preallocate a matrix to store each 300ms segment
signal_matrix = zeros(num_repetitions, signal_samples);

% Loop over each repetition to extract and store the 300ms segment
for rep = 1:num_repetitions
    start_idx = first_index + (rep - 1) * trial_samples;
    end_idx = start_idx + signal_samples - 1;
    
    % Extract the 300ms segment from y_FFR
    signal_matrix(rep, :) = y_FFR_Filtered(start_idx:end_idx);
end

%% Eliminate the 5% outliers

 %Calculate the number of samples to exclude (5% from both top and bottom)
exclude_percentage = 0.025; % 5% outliers from both ends
exclude_count = round(exclude_percentage * num_repetitions);

% Preallocate a matrix to store trimmed signals (without outliers)
trimmed_signal_matrix = zeros(num_repetitions, signal_samples);

% Loop over each repetition to remove outliers and store the trimmed data
for i = 1:signal_samples
    % Sort the values at each sample across all repetitions
    sorted_values = sort(signal_matrix(:, i));
    
    % Exclude top and bottom 5%
    trimmed_values = sorted_values(exclude_count+1:end-exclude_count);
    
    % Store the trimmed average for this sample
    trimmed_signal_matrix(:, i) = mean(trimmed_values);
end

%% Time Domain Analysis 

% Calculate the average of the 300ms segments
average_signal = mean(trimmed_signal_matrix, 1);

% Calculate the standard deviation (confidence/error estimate)
std_signal = std(signal_matrix, 0, 1);

% Calculate the standard error of the mean (SEM)
sem_signal = std_signal / sqrt(num_repetitions);

% Extract the expected signal from y_Ref (300ms from first_index)
expected_signal = y_Ref(first_index:first_index + signal_samples - 1);

% Normalize both the average signal and the expected signal
average_signal_norm = average_signal / max(abs(average_signal)); % Normalize by max value
expected_signal_norm = expected_signal / max(abs(expected_signal)); % Normalize by max value
sem_signal_norm = sem_signal / max(abs(average_signal)); % Normalize SEM by the same max

corr = abs(xcorr(average_signal_norm, expected_signal_norm, 0, 'coeff'));

%% Frequency Domain Analysis

% Frequency range
f_min = 20; % Minimum frequency (20 Hz)
f_max = 1.2 * lp_cutoff; % Maximum frequency (20% over the low-pass cutoff)

% Perform Fourier Transform
Y = fft(y_FFR_Filtered); 
n = length(y_FFR_Filtered); % Number of points in the signal

% Frequency axis
f = (0:n-1)*(fs/n); % Frequency vector

% Get the magnitude of the FFT
Y_magnitude = abs(Y/n); 

% Only keep the positive half of the spectrum
Y_magnitude = Y_magnitude(1:floor(n/2));
f = f(1:floor(n/2));

%% Jitter analysis

% Detect onsets in the reference signal (using a simple threshold method)
onset_indicies = zeros(1, num_repetitions-2);

for i = 1:num_repetitions-2
    % Calculate the absolute start and end index for each trial
    start_idx = 1+(i-1) * trial_samples;
    end_idx = start_idx + trial_samples - 1;
    
    % Find the first index where y_Ref exceeds the threshold in the segment
    relative_onset_idx = find(abs(y_FFR(start_idx:end_idx)) > abs(onset_treshold), 1);

    % Check if an onset was found; if not, set to NaN or another placeholder
    if isempty(relative_onset_idx)
        onset_indicies(i) = NaN; % Or use a different placeholder like 0
    else
        % Calculate the absolute onset index in the full y_Ref signal
        onset_indicies(i) = start_idx + relative_onset_idx - 1;
    end
end

% Calculate timing differences (jitter)
timing_differences = diff(onset_indicies(3:end)) / fs; % Convert sample differences to time (in seconds)

% Calculate jitter metrics
mean_interval = mean(timing_differences); % Mean interval
jitter_sd = std(timing_differences); % Standard deviation of intervals (jitter)
jitter_variance = var(timing_differences); % Variance of intervals
jitter_abs = mean(abs(timing_differences - mean_interval)); % Mean absolute jitter

% Display the results
disp(['Mean Interval: ', num2str(mean_interval), ' s']);
disp(['Jitter (Standard Deviation): ', num2str(jitter_sd), ' s']);
disp(['Jitter (Variance): ', num2str(jitter_variance), ' s^2']);
disp(['Jitter (Mean Absolute Deviation): ', num2str(jitter_abs), ' s']);

% Plot the timing differences to visualize jitter
figure;
stem(timing_differences);
xlabel('Repetition Number');
ylabel('Time Interval (s)');
title('Timing Differences (Jitter) in Reference Signal');
%% Plotting

FFR_Color = [0.0078, 0.1882, 0.2784];
err_Color = [0.9373, 0.1373, 0.2353];
ref_Color = [0.9843, 0.5216, 0.0000, 0.5];

% Create a figure with 2 subplots (2/3 for time-domain and 1/3 for frequency-domain)
figure;

% Subplot for the time-domain plot (occupying 2/3 of the figure)
subplot(1, 2, 1); % This allocates 2/3 of the space to the time-domain plot

% X-axis values for the plot
x_vals = 1:signal_samples;

% Plot the normalized expected signal (from y_Ref) on the same graph
plot(x_vals, expected_signal_norm, 'Color', ref_Color, 'LineWidth', 1.2); hold on;
% Plot the normalized averaged signal
plot(x_vals, average_signal_norm, 'Color', FFR_Color, 'LineWidth', 1.2); hold on;

% Fill between normalized mean ± normalized SEM to show error bars
fill([x_vals, fliplr(x_vals)], ...
     [average_signal_norm + sem_signal_norm, fliplr(average_signal_norm - sem_signal_norm)], ...
     'b', 'FaceAlpha', 0.2, 'EdgeColor', 'none');

% Customize time-domain plot
xlabel('Samples');
ylabel('Normalized Amplitude');
ylim([-1.2 1.2]); % Set Y-axis limits
title('Normalized Averaged Signal with SEM and Expected Signal from y\_Ref');

% Add legend and correlation value
leg = legend('Mean Signal (Normalized)', 'SEM', 'Expected Signal (Normalized)');
legend_text = ['Correlation = ', num2str(corr)];
title(leg, legend_text);

subplot(1, 2, 2); % 
range_idx = find(f >= f_min & f <= f_max);

% Plot the frequency representation
plot(f(range_idx), Y_magnitude(range_idx), 'LineWidth', 1.5);
xlabel('Frequency (Hz)');
ylabel('Magnitude');
title('Frequency Representation of y\_FFR\_Filtered');
xlim([f_min f_max]); % Set the x-axis limits between 20 Hz and 20% over lp_cutoff
grid on;


