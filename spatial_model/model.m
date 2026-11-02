%% pavement_load_sensor_model_full_points.m
% 3D calibration model for load positions and sensor positions
% Extended version:
%   - Builds 3D layered model
%   - Marks all load positions
%   - Draws sensor strings
%   - Automatically generates every FBG point at 0.05 m spacing
%   - Outputs:
%       1) load point table
%       2) sensor string table
%       3) full FBG point table
%
% Coordinate system:
%   Origin O = (0,0,0) at the left-bottom corner on the TOP surface
%   x: length direction, 0 -> 1.20 m
%   y: width direction, 0 -> 0.50 m
%   z: depth direction, downward is negative
%
% Author: ChatGPT

clear; clc; close all;

%% ---------------------- Basic geometry ----------------------
L = 1.20;     % length (m)
W = 0.50;     % width  (m)
H = 0.30;     % total depth (m)

zTop = 0.0;
zLayer1 = -0.08;   % concrete/asphalt top layer bottom
zLayer2 = -0.12;   % crushed stone layer bottom
zBottom = -H;

zAsphaltSensor = -0.04;
zSoilSensor    = -0.17;

sensorSpacing = 0.05; % m

%% ---------------------- Load points ----------------------
loadNames = { ...
    'Center_single'; ...
    '40kg_longitudinal_center_x30'; ...
    '40kg_longitudinal_center_x42_5'; ...
    '40kg_longitudinal_center_x90'; ...
    '40kg_longitudinal_center_x95'; ...
    'Double_symmetric_lower'; ...
    'Double_symmetric_upper'; ...
    'Double_asymmetric_p1'; ...
    'Double_asymmetric_p2'; ...
    '40kg_single_eccentric'};

loadX = [ ...
    0.60; ...
    0.30; 0.425; 0.90; 0.95; ...
    0.60; 0.60; ...
    0.40; 0.80; ...
    0.60];

loadY = [ ...
    0.25; ...
    0.25; 0.25; 0.25; 0.25; ...
    0.15; 0.35; ...
    0.15; 0.35; ...
    0.15];

loadZ = zeros(size(loadX));

loadGroup = { ...
    'Single-center'; ...
    '40kg longitudinal center line'; ...
    '40kg longitudinal center line'; ...
    '40kg longitudinal center line'; ...
    '40kg longitudinal center line'; ...
    '5/10/25/35/40kg symmetric double-point'; ...
    '5/10/25/35/40kg symmetric double-point'; ...
    '5/10/25kg asymmetric double-point'; ...
    '5/10/25kg asymmetric double-point'; ...
    '40kg single eccentric'};

loadColor = [ ...
    1 0 0; ...
    0 0.7 0; ...
    0 0.7 0; ...
    0 0.7 0; ...
    0 0.7 0; ...
    0 0.447 0.741; ...
    0.850 0.325 0.098; ...
    0.494 0.184 0.556; ...
    0.494 0.184 0.556; ...
    0 0.447 0.741];

loadTable = table(loadNames, loadGroup, loadX, loadY, loadZ, ...
    'VariableNames', {'Name','Group','X_m','Y_m','Z_m'});

%% ---------------------- Sensor strings ----------------------
% Definition rule:
%   horizontal string: start point = left endpoint
%   vertical string:   start point = bottom endpoint
%
% 6 points => 5 intervals => 0.25 m
% 8 points => 7 intervals => 0.35 m

sensorNames = {};
sensorLayer = {};
sensorType  = {};
x1 = []; y1 = []; z1 = [];
x2 = []; y2 = []; z2 = [];

% Asphalt layer
sensorNames{end+1,1} = 'SAT2-6FBGs';
sensorLayer{end+1,1} = 'Asphalt';
sensorType{end+1,1}  = 'Vertical_6pts';
x1(end+1,1) = 0.425; y1(end+1,1) = 0.125; z1(end+1,1) = zAsphaltSensor;
x2(end+1,1) = 0.425; y2(end+1,1) = 0.375; z2(end+1,1) = zAsphaltSensor;

sensorNames{end+1,1} = 'SAL2-8FBGs';
sensorLayer{end+1,1} = 'Asphalt';
sensorType{end+1,1}  = 'Horizontal_8pts';
x1(end+1,1) = 0.370; y1(end+1,1) = 0.180; z1(end+1,1) = zAsphaltSensor;
x2(end+1,1) = 0.720; y2(end+1,1) = 0.180; z2(end+1,1) = zAsphaltSensor;

sensorNames{end+1,1} = 'SAL1-8FBGs';
sensorLayer{end+1,1} = 'Asphalt';
sensorType{end+1,1}  = 'Horizontal_8pts';
x1(end+1,1) = 0.500; y1(end+1,1) = 0.250; z1(end+1,1) = zAsphaltSensor;
x2(end+1,1) = 0.850; y2(end+1,1) = 0.250; z2(end+1,1) = zAsphaltSensor;

sensorNames{end+1,1} = 'SAT1-6FBGs';
sensorLayer{end+1,1} = 'Asphalt';
sensorType{end+1,1}  = 'Vertical_6pts';
x1(end+1,1) = 1.010; y1(end+1,1) = 0.080; z1(end+1,1) = zAsphaltSensor;
x2(end+1,1) = 1.010; y2(end+1,1) = 0.330; z2(end+1,1) = zAsphaltSensor;

% Soil layer
sensorNames{end+1,1} = 'SSL1-8FBGs';
sensorLayer{end+1,1} = 'Soil';
sensorType{end+1,1}  = 'Horizontal_8pts';
x1(end+1,1) = 0.315; y1(end+1,1) = 0.250; z1(end+1,1) = zSoilSensor;
x2(end+1,1) = 0.665; y2(end+1,1) = 0.250; z2(end+1,1) = zSoilSensor;

sensorNames{end+1,1} = 'SSL2-8FBGs';
sensorLayer{end+1,1} = 'Soil';
sensorType{end+1,1}  = 'Horizontal_8pts';
x1(end+1,1) = 0.445; y1(end+1,1) = 0.195; z1(end+1,1) = zSoilSensor;
x2(end+1,1) = 0.795; y2(end+1,1) = 0.195; z2(end+1,1) = zSoilSensor;

sensorNames{end+1,1} = 'SST-6FBGs';
sensorLayer{end+1,1} = 'Soil';
sensorType{end+1,1}  = 'Vertical_6pts';
x1(end+1,1) = 0.900; y1(end+1,1) = 0.080; z1(end+1,1) = zSoilSensor;
x2(end+1,1) = 0.900; y2(end+1,1) = 0.330; z2(end+1,1) = zSoilSensor;

repX = x1;
repY = y1;
repZ = z1;

sensorTable = table(sensorNames, sensorLayer, sensorType, ...
    x1, y1, z1, x2, y2, z2, repX, repY, repZ, ...
    'VariableNames', {'Name','Layer','Type', ...
    'X_start_m','Y_start_m','Z_start_m', ...
    'X_end_m','Y_end_m','Z_end_m', ...
    'RepX_m','RepY_m','RepZ_m'});

%% ---------------------- Generate all FBG points ----------------------
pointSensor = {};
pointLayer = {};
pointIndex = [];
pointX = [];
pointY = [];
pointZ = [];

for i = 1:numel(sensorNames)
    dx = x2(i) - x1(i);
    dy = y2(i) - y1(i);
    dz = z2(i) - z1(i);
    len = sqrt(dx^2 + dy^2 + dz^2);

    nIntervals = round(len / sensorSpacing);
    nPoints = nIntervals + 1;

    xs = linspace(x1(i), x2(i), nPoints);
    ys = linspace(y1(i), y2(i), nPoints);
    zs = linspace(z1(i), z2(i), nPoints);

    for k = 1:nPoints
        pointSensor{end+1,1} = sensorNames{i};
        pointLayer{end+1,1} = sensorLayer{i};
        pointIndex(end+1,1) = k;
        pointX(end+1,1) = xs(k);
        pointY(end+1,1) = ys(k);
        pointZ(end+1,1) = zs(k);
    end
end

pointName = strcat(pointSensor, "_P", string(pointIndex));

fbgPointTable = table(pointName, pointSensor, pointLayer, pointIndex, ...
    pointX, pointY, pointZ, ...
    'VariableNames', {'PointName','SensorName','Layer','PointIndex','X_m','Y_m','Z_m'});

%% ---------------------- 3D plot ----------------------
fig = figure('Color','w','Position',[80 60 1400 850]);
hold on; grid on; box on;
view(38, 22);

drawLayerBlock(L, W, zTop, zLayer1, [0.75 0.75 0.75], 0.35);
drawLayerBlock(L, W, zLayer1, zLayer2, [0.70 0.80 0.95], 0.35);
drawLayerBlock(L, W, zLayer2, zBottom, [0.65 0.55 0.20], 0.35);

plot3([0 L L 0 0], [0 0 W W 0], [0 0 0 0 0], 'k-', 'LineWidth', 1.3);

% Draw sensor strings and representative points
for i = 1:numel(sensorNames)
    plot3([x1(i) x2(i)], [y1(i) y2(i)], [z1(i) z2(i)], ...
        '--', 'Color', [1 1 0], 'LineWidth', 3);

    scatter3(repX(i), repY(i), repZ(i), 70, 'filled', ...
        'MarkerFaceColor', [1 0.85 0], 'MarkerEdgeColor', 'k');

    text(repX(i)+0.01, repY(i)+0.01, repZ(i), sensorNames{i}, ...
        'FontSize', 10, 'Interpreter', 'none');
end

% Draw all FBG points
scatter3(pointX, pointY, pointZ, 28, 'filled', ...
    'MarkerFaceColor', [1 1 0.2], 'MarkerEdgeColor', 'k');

% Draw load points
for i = 1:height(loadTable)
    scatter3(loadX(i), loadY(i), loadZ(i)+0.003, 120, '^', 'filled', ...
        'MarkerFaceColor', loadColor(i,:), 'MarkerEdgeColor', 'k');
end

text(0.60, 0.25, 0.02, 'Center single', 'Color', [1 0 0], ...
    'FontWeight', 'bold', 'HorizontalAlignment', 'center');
text(0.28, 0.28, 0.02, '40kg longitudinal centers', 'Color', [0 0.6 0], ...
    'FontWeight', 'bold');
text(0.61, 0.15, 0.02, 'Symmetric double', 'Color', [0 0.447 0.741], ...
    'FontWeight', 'bold');
text(0.80, 0.35, 0.02, 'Asymmetric double', 'Color', [0.494 0.184 0.556], ...
    'FontWeight', 'bold');

% Axes
quiver3(0,0,0,0.18,0,0,0,'r','LineWidth',2,'MaxHeadSize',0.6);
quiver3(0,0,0,0,0.12,0,0,'g','LineWidth',2,'MaxHeadSize',0.6);
quiver3(0,0,0,0,0,-0.08,0,'b','LineWidth',2,'MaxHeadSize',0.6);
text(0.19,0,0,'X','Color','r','FontWeight','bold','FontSize',12);
text(0,0.13,0,'Y','Color','g','FontWeight','bold','FontSize',12);
text(0,0,-0.09,'Z (down)','Color','b','FontWeight','bold','FontSize',12);

xlabel('X (m) - length direction');
ylabel('Y (m) - width direction');
zlabel('Z (m) - depth direction');
title('3D model of load positions and full FBG point coordinates');

axis equal;
xlim([0 L]);
ylim([0 W]);
zlim([zBottom 0.05]);

%% ---------------------- 2D top view ----------------------
figure('Color','w','Position',[80 120 1350 560]);

subplot(1,2,1); hold on; box on; grid on;
rectangle('Position',[0 0 L W], 'EdgeColor','k', 'LineWidth',1.2);

for i = 1:numel(sensorNames)
    plot([x1(i) x2(i)], [y1(i) y2(i)], '--', 'Color', [1 0.8 0], 'LineWidth', 3);
    scatter(repX(i), repY(i), 45, 'filled', 'MarkerFaceColor', [1 0.85 0], 'MarkerEdgeColor', 'k');
end

scatter(pointX, pointY, 30, 'filled', 'MarkerFaceColor', [1 1 0.2], 'MarkerEdgeColor', 'k');

for i = 1:height(loadTable)
    scatter(loadX(i), loadY(i), 75, '^', 'filled', ...
        'MarkerFaceColor', loadColor(i,:), 'MarkerEdgeColor', 'k');
end

for i = 1:height(fbgPointTable)
    text(pointX(i)+0.006, pointY(i)+0.004, sprintf('%d', pointIndex(i)), ...
        'FontSize', 7, 'Color', [0.2 0.2 0.2]);
end

xlabel('X (m)');
ylabel('Y (m)');
title('Top view: load points, sensor strings and all FBG points');
axis equal;
xlim([0 L]); ylim([0 W]);

subplot(1,2,2); hold on; box on; grid on;
plot([0 L],[zAsphaltSensor zAsphaltSensor],'k--','LineWidth',1.2);
plot([0 L],[zSoilSensor zSoilSensor],'k--','LineWidth',1.2);

for i = 1:height(fbgPointTable)
    scatter(pointX(i), pointZ(i), 26, 'filled', 'MarkerFaceColor', [1 1 0.2], 'MarkerEdgeColor', 'k');
end

xlabel('X (m)');
ylabel('Z (m)');
title('X-Z view of all FBG points');
xlim([0 L]);
ylim([zBottom 0.02]);

%% ---------------------- Console output ----------------------
disp('================ Load point coordinates ================');
disp(loadTable);

disp('================ Sensor string coordinates =============');
disp(sensorTable);

disp('================ All FBG point coordinates =============');
disp(fbgPointTable);

%% ---------------------- Export tables ----------------------
writetable(loadTable, 'load_points_coordinates.csv');
writetable(sensorTable, 'sensor_coordinates.csv');
writetable(fbgPointTable, 'all_fbg_points_coordinates.csv');

fprintf('\nCSV files exported:\n');
fprintf('  - load_points_coordinates.csv\n');
fprintf('  - sensor_coordinates.csv\n');
fprintf('  - all_fbg_points_coordinates.csv\n');

%% ---------------------- Local function ----------------------
function drawLayerBlock(L, W, zTop, zBot, faceColor, faceAlpha)
    V = [ ...
        0 0 zTop;
        L 0 zTop;
        L W zTop;
        0 W zTop;
        0 0 zBot;
        L 0 zBot;
        L W zBot;
        0 W zBot];
    F = [ ...
        1 2 3 4;
        5 6 7 8;
        1 2 6 5;
        2 3 7 6;
        3 4 8 7;
        4 1 5 8];
    patch('Vertices',V, 'Faces',F, ...
        'FaceColor',faceColor, 'FaceAlpha',faceAlpha, ...
        'EdgeColor',[0.35 0.35 0.35], 'LineWidth',0.8);
end
