[vel_rec_Low,fs] = audioread("Analysis/AccelLow.wav");
[vel_rec_High,fs] = audioread("Analysis/AccelHigh.wav");

T = 1 / fs; % Sampling period in seconds

input_sensitivity = 10.2; % mV /m /s
low_measure = 58; % mV p2p
high_measure = 98; % mV p2p

time_low = (0:length(vel_rec_Low)-1) / fs;
time_high = (0:length(vel_rec_High)-1) / fs;

scale_factor_low = (low_measure / 2) / input_sensitivity; % m/s per unit
scale_factor_high = (high_measure / 2) / input_sensitivity; % m/s per unit

vel_low_scaled = vel_rec_Low * scale_factor_low; % m/s
vel_high_scaled = vel_rec_High * scale_factor_high; % m/s

accel_low = gradient(vel_low_scaled, time_low); % m/s/s
accel_high = gradient(vel_high_scaled, time_high);  % m/s/s

% Divide by Fs to get back to m/s/s acccurately.

% experiments

velocity = vel_rec_Low / T; %m/s
Acceleration = diff(velocity) / T;


% Figures 
figure;
subplot(2,1,1);
plot(time_low, vel_low_scaled);
xlabel('Time (s)');
ylabel('Velocity (m/s)');
title('Low Measurement: Velocity vs Time');

subplot(2,1,2);
plot(time_low, accel_low);
xlabel('Time (s)');
ylabel('Acceleration (m/s^2)');
title('Low Measurement: Acceleration vs Time');

figure;
subplot(2,1,1);
plot(time_high, vel_high_scaled);
xlabel('Time (s)');
ylabel('Velocity (m/s)');
title('High Measurement: Velocity vs Time');

subplot(2,1,2);
plot(time_high, accel_high);
xlabel('Time (s)');
ylabel('Acceleration (m/s^2)');
title('High Measurement: Acceleration vs Time');