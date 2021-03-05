function data = fun_regionalization(region)
%% Regional data that will be imported by the taxonomy script
% Regions:
% 1 - West Coast - temperate
% 2 - North Central/Northeast - cold/cold
% 3 - Southwest - hot/arid
% 4 - Southeast/Central - hot/cold
% 5 - Southeast coastal - hot/humid
% 6 - Hawaii - sub-tropical (not part of original taxonomy)

%% Regional building data
% TODO: Region 6 is unknown right now
% thermal_percentage integrity percentages
%   {region}(level,sf/apart/mh)
%   single family homes
%   apartments
%   mobile homes
%   level corresponds to age of home from "Building Reccs"
%       1:pre-1940, 2:1940-1949, 3:1950-1959, 4:1960-1969, 5:1970-1979, 6:1980-1989, 7:1990-2005
%       1:pre-1960, 2:1960-1989, 3:1990-2005
%       1:pre-1960, 2:1960-1989, 3:1990-2005
thermal_percentage{1} = [   0.0805,0.0724,0.1090,0.0867,0.1384,0.1264,0.1297;
                            0.0356,0.1223,0.0256,0.0000,0.0000,0.0000,0.0000;
                            0.0000,0.0554,0.0181,0.0000,0.0000,0.0000,0.0000];
thermal_percentage{2} = [   0.1574,0.0702,0.1290,0.0971,0.0941,0.0744,0.1532;
                            0.0481,0.0887,0.0303,0.0000,0.0000,0.0000,0.0000;
                            0.0000,0.0372,0.0202,0.0000,0.0000,0.0000,0.0000];
thermal_percentage{3} = [   0.0448,0.0252,0.0883,0.0843,0.1185,0.1315,0.2411;
                            0.0198,0.1159,0.0478,0.0000,0.0000,0.0000,0.0000;
                            0.0000,0.0524,0.0302,0.0000,0.0000,0.0000,0.0000];
thermal_percentage{4} = [   0.0526,0.0337,0.0806,0.0827,0.1081,0.1249,0.2539;
                            0.0217,0.1091,0.0502,0.0000,0.0000,0.0000,0.0000;
                            0.0000,0.0491,0.0333,0.0000,0.0000,0.0000,0.0000];
thermal_percentage{5} = [   0.0526,0.0337,0.0806,0.0827,0.1081,0.1249,0.2539;
                            0.0217,0.1091,0.0502,0.0000,0.0000,0.0000,0.0000;
                            0.0000,0.0491,0.0333,0.0000,0.0000,0.0000,0.0000];
thermal_percentage{6} = [   0.0526,0.0337,0.0806,0.0827,0.1081,0.1249,0.2539;
                            0.0217,0.1091,0.0502,0.0000,0.0000,0.0000,0.0000;
                            0.0000,0.0491,0.0333,0.0000,0.0000,0.0000,0.0000];
                        
for jjj=1:6
    check_total = sum(sum(thermal_percentage{jjj}));
    if ( abs(check_total - 1) > 0.001 )
        error(['Error in total thermal percentage{',num2str(jjj),'} - Sum does not equal 100%.']);
    end
end

% thermal properties for each level
%   {sf/apart/mh,level}(R-ceil,R-wall,R-floor,window layers,window glass, glazing treatment, window frame, R-door, Air infiltration, COP high, COP low)
%   Single family homes
thermal_properties{1,1} =  [16.0, 10.0, 10.0, 1, 1, 1, 1,   3,  .75, 2.8, 2.4];
thermal_properties{1,2} =  [19.0, 11.0, 12.0, 2, 1, 1, 1,   3,  .75, 3.0, 2.5];
thermal_properties{1,3} =  [19.0, 14.0, 16.0, 2, 1, 1, 1,   3,   .5, 3.2, 2.6];
thermal_properties{1,4} =  [30.0, 17.0, 19.0, 2, 1, 1, 2,   3,   .5, 3.4, 2.8];
thermal_properties{1,5} =  [34.0, 19.0, 20.0, 2, 1, 1, 2,   3,   .5, 3.6, 3.0];
thermal_properties{1,6} =  [36.0, 22.0, 22.0, 2, 2, 1, 2,   5, 0.25, 3.8, 3.0];
thermal_properties{1,7} =  [48.0, 28.0, 30.0, 3, 2, 2, 4,  11, 0.25, 4.0, 3.0];
%   Apartments
thermal_properties{2,1} =  [13.4, 11.7,  9.4, 1, 1, 1, 1, 2.2, .75, 2.8, 1.9];
thermal_properties{2,2} =  [20.3, 11.7, 12.7, 2, 1, 2, 2, 2.7, 0.25, 3.0, 2.0];
thermal_properties{2,3} =  [28.7, 14.3, 12.7, 2, 2, 3, 4, 6.3, .125, 3.2, 2.1];
%   Mobile Homes
thermal_properties{3,1} =  [   0,    0,    0, 0, 0, 0, 0,   0,   0,   0,   0];
thermal_properties{3,2} =  [13.4,  9.2, 11.7, 1, 1, 1, 1, 2.2, .75, 2.8, 1.9];
thermal_properties{3,3} =  [24.1, 11.7, 18.1, 2, 2, 1, 2,   3, .75, 3.5, 2.2];

% Average floor areas for each type and region
% TODO: Region 6 is unknown right now
floor_area{1} = [2209,820,1054];
floor_area{2} = [2951,798,1035];
floor_area{3} = [2370,764,1093];
floor_area{4} = [2655,901,1069];
floor_area{5} = [2655,901,1069];
floor_area{6} = [2655,901,1069];

% Percentage of one-story homes
% TODO: Region 6 is unknown right now
one_story = [.6887;.5210;.7745;.7043;.7043;.7043];

% Average heating and cooling setpoints
%  by thermal integrity type {1=SF, 2=apt, 3=mh}
%  [nighttime percentage, nighttime average difference (+ indicates nightime
%  is cooler), high bin value, low bin value]
cooling_setpoint{1} = [ 0.098,0.96,69,65;
                        0.140,0.96,70,70;
                        0.166,0.96,73,71;
                        0.306,0.96,76,74;
                        0.206,0.96,79,77;
                        0.084,0.96,85,80];
                    
cooling_setpoint{2} = [ 0.155,0.49,69,65;
                        0.207,0.49,70,70;
                        0.103,0.49,73,71;
                        0.310,0.49,76,74;
                        0.155,0.49,79,77;
                        0.069,0.49,85,80];
                    
cooling_setpoint{3} = [ 0.138,0.97,69,65;
                        0.172,0.97,70,70;
                        0.172,0.97,73,71;
                        0.276,0.97,76,74;
                        0.138,0.97,79,77;
                        0.103,0.97,85,80];
                    
heating_setpoint{1} = [ 0.141,0.80,63,59;
                        0.204,0.80,66,64;
                        0.231,0.80,69,67;
                        0.163,0.80,70,70;
                        0.120,0.80,73,71;
                        0.141,0.80,79,74];

heating_setpoint{2} = [ 0.085,0.20,63,59;
                        0.132,0.20,66,64;
                        0.147,0.20,69,67;
                        0.279,0.20,70,70;
                        0.109,0.20,73,71;
                        0.248,0.20,79,74];
                    
heating_setpoint{3} = [ 0.129,0.88,63,59;
                        0.177,0.88,66,64;
                        0.161,0.88,69,67;
                        0.274,0.88,70,70;
                        0.081,0.88,73,71;
                        0.177,0.88,79,74];
                    
% Breakdown of gas vs. heat pump vs. resistance - by region
% TODO: Region 6 is unknown right now
% perc_gas = [0.7051;0.8927;0.6723;0.4425;0.4425;0.4425];
% perc_pump = [0.0321;0.0177;0.0559;0.1983;0.1983;0.1983];
perc_gas = [0.031;0.8927;0.6723;0.4425;0.4425;0.4425];
perc_pump = [0.0121;0.0177;0.0559;0.1983;0.1983;0.1983];
perc_res = 1 - perc_pump - perc_gas;

% of AC 
% TODO: Region 6 is unknown right now
perc_AC = [0.4348;0.7528;0.5259;0.9673;0.9673;0.9673];

% Over sizing factor of the AC units
% TODO: Region 6 is unknown right now
over_sizing_factor = [0.1;0.2;0.2;0.3;0.3;0.3];

% pool pumps
% TODO: Region 6 is unknown right now
perc_poolpumps = [0.0904;0.0591;0.0818;0.0657;0.0657;0.0657];

% water heaters
% Breakdown by fuel vs. electric
% TODO: Region 6 is unknown right now
wh_electric = [0.7455;0.7485;0.6520;0.3572;0.3572;0.3572];

% size of units - [<30, 31-49, >50] - by region
% TODO: Region 6 is unknown right now
wh_size = [ 0.0000,0.3333,0.6667;
            0.1459,0.5836,0.2706;
            0.2072,0.5135,0.2793;
            0.2259,0.5267,0.2475;
            0.2259,0.5267,0.2475;
            0.2259,0.5267,0.2475];

% emission dispatch order
% Nuc Hydro Solar BioMass Wind Coal NG GeoTherm Petro
% TODO: Region 6 is unknown right now
dispatch_order = [1,5,2,3,4,7,6,8,9;
                  1,7,2,3,4,5,6,8,9;
                  1,7,2,3,4,5,6,8,9;
                  1,7,2,3,4,5,6,8,9;
                  1,7,2,3,4,6,5,8,9;
                  1,7,2,3,4,6,5,8,9];


data.thermal_properties = thermal_properties;
data.thermal_percentages = thermal_percentage{region};
data.cooling_setpoint = cooling_setpoint;
data.heating_setpoint = heating_setpoint;
data.perc_gas = perc_gas(region);
data.perc_pump = perc_pump(region);
data.perc_res = perc_res(region);
data.perc_AC = perc_AC(region);
data.perc_poolpumps = perc_poolpumps(region);
data.floor_area = floor_area{region};
data.perc_poolpumps = perc_poolpumps(region);
data.wh_electric = wh_electric(region);
data.wh_size = wh_size(region,:);
data.no_cool_sch = 8;
data.no_heat_sch = 6;
data.no_water_sch = 6;
data.one_story = one_story;
data.over_sizing_factor = over_sizing_factor(region);
data.dispatch_order = dispatch_order(region,:);

%Other parameters

%Percentage small homes on the feeder (versus large homes)
data.percentageSmall=0.50;

% Skews
data.residential_skew_std = 2700;
data.residential_skew_max = 8100;
data.commercial_skew_std = 1800; %These are in 30 minute blocks
data.commercial_skew_max = 5400;

%% Residential parameters from technology parameters
% ZIP fractions and their power factors - Residential
data.z_pf = 1;
data.i_pf = 1;
data.p_pf = 1;
data.zfrac = 0.2;
data.ifrac = 0.4;
data.pfrac = 1 - data.zfrac - data.ifrac;

data.heat_fraction = 0.9;

% waterheaters 1 = yes, 0 = no
data.use_wh = 1; 
data.res_meter_cons = 0;

%Slider setting-related item from technology file (no idea what this is)
data.market_info=1.0;

% There is no ZIP fraction assosciated with this variable
data.light_scalar_res = 1;

%Generator controller object information
% { rating (kW), start state, bid_curve text, startup cost, shutdown_cost, min runtime, min downtime, amortizaiton factor (1/h)}
data.GenControlInformation = {
    {30, 'OFF', '5 25.00 6 26.00 7 26.5 8 27 9 27.50 10 28 11 28.50 12 29 20 30.0 30 45.00', 15.00, 5.00, 35.0, 0.0, 5};
    {30, 'OFF', '5 25.00 6 26.00 7 26.5 8 27 9 27.50 10 28 11 28.50 12 29 20 30.0 30 45.00', 15.00, 5.00, 35.0, 0.0, 5};
    {30, 'OFF', '5 25.00 6 26.00 7 26.5 8 27 9 27.50 10 28 11 28.50 12 29 20 30.0 30 45.00', 15.00, 5.00, 35.0, 0.0, 5};
    {30, 'OFF', '5 25.00 6 26.00 7 26.5 8 27 9 27.50 10 28 11 28.50 12 29 20 30.0 30 45.00', 15.00, 5.00, 35.0, 0.0, 5};
    {30, 'OFF', '5 25.00 6 26.00 7 26.5 8 27 9 27.50 10 28 11 28.50 12 29 20 30.0 30 45.00', 15.00, 5.00, 35.0, 0.0, 5};
    {30, 'OFF', '5 25.00 6 26.00 7 26.5 8 27 9 27.50 10 28 11 28.50 12 29 20 30.0 30 45.00', 15.00, 5.00, 35.0, 0.0, 5};
    {30, 'OFF', '5 25.00 6 26.00 7 26.5 8 27 9 27.50 10 28 11 28.50 12 29 20 30.0 30 45.00', 15.00, 5.00, 35.0, 0.0, 5};
};
