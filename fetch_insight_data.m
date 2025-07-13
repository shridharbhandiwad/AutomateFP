%% Fetch Insight Data Script
% This script processes subset data to find activation cycles and extract
% fusObj ID and dep ID information

%% Step 1: Find activation and cycle using provided formulas
fprintf('Step 1: Calculating activation flags and cycles...\n');

% Calculate activation flags
activation_flags = SfRunMainProc_m_portMainProc_out.m_brakeTypeActive | ...
                  SfRunMainProc_debugvariables.m_stateMachines.m_hbaStateMachine.m_currentState;

% Calculate cycles using interpolation
cycles = interp1(g_PerSpdRunnable_m_syncInfoPort_out.time, ...
                1:length(g_PerSpdRunnable_m_syncInfoPort_out.time), ...
                SfRunMainProc_m_portMainProc_out.time, ...
                'nearest', 'extrap');

% Find first activation cycle
first_activation_idx = find(activation_flags, 1);
if isempty(first_activation_idx)
    error('No activation found in the data');
end

first_activation_cycle = cycles(first_activation_idx);

fprintf('First activation found at cycle: %d\n', first_activation_cycle);

%% Step 2: Plot activation flags
fprintf('Step 2: Plotting activation flags...\n');

figure;
stem(cycles, activation_flags);
title(['Brake activations (1st @ cycle ', num2str(first_activation_cycle), ' \pm 1)']);
xlabel('# cycle');
ylabel('Activation flag');
grid on;

%% Step 3: Extract fusObj ID and dep ID for the found cycle
fprintf('Step 3: Extracting fusObj ID and dep ID for cycle %d...\n', first_activation_cycle);

% Find the time index corresponding to the first activation cycle
activation_time_idx = first_activation_idx;

% Extract fusObj ID from EdimTprRunnable data
% Note: Assuming EdimTprRunnable has time-synchronized data
try
    % Find the corresponding index in EdimTprRunnable data
    if exist('EdimTprRunnable', 'var') && isfield(EdimTprRunnable, 'time')
        % Find closest time match
        [~, edim_idx] = min(abs(EdimTprRunnable.time - SfRunMainProc_m_portMainProc_out.time(activation_time_idx)));
        
        % Extract fusObj ID (assuming it's in a field like fusObj or objectID)
        if isfield(EdimTprRunnable, 'fusObj')
            fusObj_id = EdimTprRunnable.fusObj(edim_idx);
        elseif isfield(EdimTprRunnable, 'objectID')
            fusObj_id = EdimTprRunnable.objectID(edim_idx);
        elseif isfield(EdimTprRunnable, 'fusObjID')
            fusObj_id = EdimTprRunnable.fusObjID(edim_idx);
        else
            % Look for any field containing 'fus' or 'obj'
            fields = fieldnames(EdimTprRunnable);
            fus_fields = fields(contains(fields, 'fus', 'IgnoreCase', true) | ...
                               contains(fields, 'obj', 'IgnoreCase', true));
            if ~isempty(fus_fields)
                fusObj_id = EdimTprRunnable.(fus_fields{1})(edim_idx);
            else
                warning('Could not find fusObj ID field in EdimTprRunnable');
                fusObj_id = NaN;
            end
        end
    else
        warning('EdimTprRunnable data not found or missing time field');
        fusObj_id = NaN;
    end
catch ME
    warning('Error extracting fusObj ID: %s', ME.message);
    fusObj_id = NaN;
end

% Extract dep ID from depRunnable dep port out
try
    % Find the corresponding index in depRunnable data
    if exist('depRunnable', 'var') && isfield(depRunnable, 'dep_port_out')
        dep_port_out = depRunnable.dep_port_out;
        
        if isfield(dep_port_out, 'time')
            % Find closest time match
            [~, dep_idx] = min(abs(dep_port_out.time - SfRunMainProc_m_portMainProc_out.time(activation_time_idx)));
            
            % Extract dep ID (assuming it's in a field like depID, id, or objectID)
            if isfield(dep_port_out, 'depID')
                dep_id = dep_port_out.depID(dep_idx);
            elseif isfield(dep_port_out, 'id')
                dep_id = dep_port_out.id(dep_idx);
            elseif isfield(dep_port_out, 'objectID')
                dep_id = dep_port_out.objectID(dep_idx);
            else
                % Look for any field containing 'dep' or 'id'
                fields = fieldnames(dep_port_out);
                dep_fields = fields(contains(fields, 'dep', 'IgnoreCase', true) | ...
                                   contains(fields, 'id', 'IgnoreCase', true));
                if ~isempty(dep_fields)
                    dep_id = dep_port_out.(dep_fields{1})(dep_idx);
                else
                    warning('Could not find dep ID field in depRunnable.dep_port_out');
                    dep_id = NaN;
                end
            end
        else
            warning('depRunnable.dep_port_out missing time field');
            dep_id = NaN;
        end
    else
        warning('depRunnable.dep_port_out data not found');
        dep_id = NaN;
    end
catch ME
    warning('Error extracting dep ID: %s', ME.message);
    dep_id = NaN;
end

%% Step 4: Display results
fprintf('\n=== INSIGHT DATA RESULTS ===\n');
fprintf('First activation cycle: %d\n', first_activation_cycle);
fprintf('Activation time index: %d\n', activation_time_idx);
fprintf('fusObj ID: %s\n', num2str(fusObj_id));
fprintf('dep ID: %s\n', num2str(dep_id));

% Create a results structure
insight_data = struct();
insight_data.first_activation_cycle = first_activation_cycle;
insight_data.activation_time_idx = activation_time_idx;
insight_data.fusObj_id = fusObj_id;
insight_data.dep_id = dep_id;
insight_data.activation_flags = activation_flags;
insight_data.cycles = cycles;

% Save results to workspace
assignin('base', 'insight_data', insight_data);
fprintf('\nResults saved to workspace variable: insight_data\n');

%% Optional: Display additional information about the activation cycle
fprintf('\n=== ADDITIONAL CYCLE INFORMATION ===\n');
if activation_time_idx > 0 && activation_time_idx <= length(SfRunMainProc_m_portMainProc_out.time)
    fprintf('Activation time: %.6f s\n', SfRunMainProc_m_portMainProc_out.time(activation_time_idx));
    
    % Show a window around the activation
    window_size = 5;
    start_idx = max(1, activation_time_idx - window_size);
    end_idx = min(length(activation_flags), activation_time_idx + window_size);
    
    fprintf('Activation flags around cycle %d:\n', first_activation_cycle);
    for i = start_idx:end_idx
        marker = '';
        if i == activation_time_idx
            marker = ' <-- ACTIVATION';
        end
        fprintf('  Cycle %d (idx %d): %d%s\n', cycles(i), i, activation_flags(i), marker);
    end
end