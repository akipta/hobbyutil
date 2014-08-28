'''

Bugs:

    - The -t option doesn't work correctly.  Try '-t 1 steel' and -t
      100 steel' -- you get the same results.  It works ok with
      numerical arguments.

    - '-u steel' doesn't work like the manpage says.

Utility to find density of materials by name or value.  Run with no
command line argument to get a manpage.  Also see the density.pdf
file that came in the density.zip package.
 
-----------------------------------------------------------------
Copyright (C) 2005, 2013 Don Peterson
Contact:  gmail.com@someonesdad1
 
The Wide Open License (WOL)
 
Permission to use, copy, modify, distribute and sell this
software and its documentation for any purpose is hereby granted
without fee, provided that the above copyright notice and this
license appear in all source copies.  THIS SOFTWARE IS PROVIDED
"AS IS" WITHOUT EXPRESS OR IMPLIED WARRANTY OF ANY KIND. See
http://www.dspguru.com/wide-open-license for more information.
'''
import sys, os, getopt, re
from sig import sig

from pdb import set_trace as xx
if 0:
    import debug
    debug.SetDebugger()


# The following variable, if True, causes the data from reference sim
# to be ignored.  I added this feature after examining the output
# sorted by density, which leads me to believe that most (but not all)
# of the data from reference sim was copied from reference glo.
# Ignoring reference sim's data will remove about 550 densities.
ignore_ref_sim = True

# The following density information came from a variety of sources.
# See the material following this table for the details on the
# references.
data = '''
# Name                                           g/cc          Ref

category = metal
Alnico                                         ; 6.9-7.2     ; aes 308
Alnico I                                       ; 6.89        ; asm 52
Aluminum                                       ; 2.64        ; glo 390
Aluminum                                       ; 2.698       ; el
Aluminum                                       ; 2.7         ; pht
Aluminum                                       ; 2.70        ; aes 117
Aluminum                                       ; 2.70        ; mh 2270
Aluminum bronze (3-10% Al)                     ; 7.7-8.7     ; sim
Aluminum foil                                  ; 2.7-2.75    ; sim
Aluminum, 2024 alloy                           ; 2.77        ; asm 52
Aluminum, 5052 alloy                           ; 2.68        ; asm 52
Aluminum, 6061 alloy                           ; 2.70        ; asm 52
Aluminum, 99.996%                              ; 2.6989      ; asm 52
Aluminum, liquid at melting point              ; 2.39        ; hcp B263
Aluminum, melted                               ; 2.56-2.64   ; sim
Antimony                                       ; 6.618       ; mh 2270
Antimony                                       ; 6.62        ; asm 52
Antimony                                       ; 6.69        ; aes 117
Antimony                                       ; 6.691       ; el
Antimony, cast                                 ; 6.696       ; sim
Antimony, cast                                 ; 6.7         ; glo 390
Babbitt                                        ; 7.272       ; sim
Babbitt                                        ; 7.28        ; glo 390
Babbitt, lead-based, SAE 13                    ; 10.24       ; asm 52
Barium                                         ; 3.594       ; el
Barium                                         ; 3.78        ; glo 390
Barium                                         ; 3.78        ; mh 2270
Barium                                         ; 3.78        ; sim
Beryllium                                      ; 1.84        ; sim
Beryllium                                      ; 1.8477      ; el
Beryllium                                      ; 1.848       ; asm 52
Beryllium                                      ; 1.85        ; aes 117
Beryllium copper                               ; 8.1-8.25    ; sim
Beryllium copper                               ; 8.25        ; aes 118
Beryllium wire                                 ; 1.85        ; aes 182
Beryllium-copper                               ; 8.23        ; asm 52
Bismuth                                        ; 9.747       ; el
Bismuth                                        ; 9.75        ; aes 117
Bismuth                                        ; 9.781       ; mh 2270
Bismuth                                        ; 9.787       ; sim
Bismuth                                        ; 9.79        ; glo 390
Bismuth                                        ; 9.80        ; asm 52
Boron                                          ; 2.535       ; mh 2270
Brass                                          ; 8.56        ; glo 390
Brass, 50 Cu, 50 Zn                            ; 8.20        ; mh 2270
Brass, 60 Cu, 40 Zn                            ; 8.36        ; mh 2270
Brass, 70 Cu, 30 Zn                            ; 8.44        ; mh 2270
Brass, 80 Cu, 20 Zn                            ; 8.60        ; mh 2270
Brass, cartridge 70%                           ; 8.53        ; asm 52
Brass, cast                                    ; 8.4-8.7     ; sim
Brass, leaded free-machining                   ; 8.50        ; asm 52
Brass, naval                                   ; 8.44        ; asm 52
Brass, red (cast)                              ; 8.7         ; aes 118
Brass, red 85%                                 ; 8.75        ; asm 52
Brass, rolled and drawn                        ; 8.43-8.73   ; sim
Brass, yellow (high brass)                     ; 8.47        ; aes 118
Bronze                                         ; 8.16        ; glo 390
Bronze (8-14% tin)                             ; 7.4-8.9     ; sim
Bronze, 90 Cu, 10 Sn                           ; 8.78        ; mh 2270
Bronze, lead                                   ; 7.7-8.7     ; sim
Bronze, phosphor                               ; 8.88        ; mar 6-7
Bronze, phosphor, 8%                           ; 8.80        ; asm 52
Bronze, phosphorous                            ; 8.78-8.92   ; sim
Cadmium                                        ; 8.648       ; mh 2270
Cadmium                                        ; 8.65        ; aes 117
Cadmium                                        ; 8.65        ; asm 52
Cadmium                                        ; 8.65        ; glo 390
Cadmium                                        ; 8.65        ; sim
Cadmium                                        ; 8.650       ; el
Calcium                                        ; 1.54        ; mh 2270
Calcium                                        ; 1.55        ; asm 52
Calcium                                        ; 1.550       ; el
Cerium                                         ; 6.771       ; aes 129
Cerium (alpha)                                 ; 8.240       ; el
Cerium (beta)                                  ; 6.749       ; el
Cerium (delta)                                 ; 6.700       ; el
Cerium (gamma)                                 ; 6.773       ; el
Cesium                                         ; 1.873       ; el
Cesium                                         ; 1.903       ; asm 52
Chrome, liquid at melting point                ; 6.46        ; hcp B263
Chromel (90Ni-10Cr)                            ; 8.5         ; wp
Chromium                                       ; 6.856       ; sim
Chromium                                       ; 6.86        ; glo 390
Chromium                                       ; 6.93        ; mh 2270
Chromium                                       ; 7.19        ; asm 52
Chromium                                       ; 7.190       ; el
Chromium                                       ; 7.2         ; aes 117
Chromium                                       ; 7.20        ; aes 120
Cobalt                                         ; 8.71        ; mh 2270
Cobalt                                         ; 8.746       ; sim
Cobalt                                         ; 8.75        ; glo 390
Cobalt                                         ; 8.85        ; asm 52
Cobalt                                         ; 8.9         ; aes 117
Cobalt                                         ; 8.9         ; aes 120
Cobalt                                         ; 8.900       ; el
Cobalt, liquid at melting point                ; 7.67        ; hcp B263
Constantan                                     ; 8.9         ; asm 52
Constantan (cupronickel 55-45)                 ; 8.9         ; aes 118
Copper                                         ; 8.89        ; mh 2270
Copper                                         ; 8.91        ; aes 118
Copper                                         ; 8.93        ; sim
Copper                                         ; 8.96        ; aes 117
Copper                                         ; 8.960       ; el
Copper                                         ; 8.96        ; pht
Copper ore, pyrites                            ; 4.1-4.3     ; mar 6-7
Copper, OFHC                                   ; 8.94        ; web
Copper, cast                                   ; 8.69        ; glo 390
Copper, cast or rolled                         ; 8.8-8.95    ; mar 6-7
Copper, liquid at melting point                ; 7.94        ; hcp B263
Copper, pure                                   ; 8.96        ; asm 52
Copper, rolled                                 ; 8.91        ; glo 390
Curium                                         ; 13.300      ; el
Delta metal (brass alloy:  55 Cu, 42 Zn, 2 Fe) ; 8.6         ; sim
Dysprosium                                     ; 8.540       ; aes 129
Dysprosium                                     ; 8.550       ; el
Electrum (40-50% gold, balance mostly silver)  ; 8.4-8.9     ; sim
Erbium                                         ; 9.045       ; aes 129
Erbium                                         ; 9.066       ; el
Europium                                       ; 5.243       ; el
Europium                                       ; 5.253       ; aes 129
Gadolinium                                     ; 7.898       ; aes 129
Gadolinium                                     ; 7.9004      ; el
Galena (lead ore, PbS)                         ; 7.3-7.6     ; mar 6-7
Gallium                                        ; 5.907       ; asm 52
Gallium                                        ; 5.907       ; el
German silver (nickel silver)                  ; 8.58        ; mar 6-7
Germanium                                      ; 5.323       ; asm 52
Gold                                           ; 19.3        ; mh 2270
Gold                                           ; 19.32       ; aes 117
Gold                                           ; 19.32       ; asm 52
Gold                                           ; 19.32       ; sim
Gold                                           ; 19.320      ; el
Gold                                           ; 19.3      ; pht
Gold coin, US                                  ; 17.18-17.2  ; mar 6-7
Gold, liquid at melting point                  ; 17.3        ; hcp B263
Gold, pure                                     ; 19.29       ; glo 390
Hafnium                                        ; 13.1        ; asm 52
Hafnium                                        ; 13.3        ; aes 120
Hafnium                                        ; 13.310      ; el
Holmium                                        ; 8.781       ; aes 129
Holmium                                        ; 8.795       ; el
Inconel X (Ni-Cr-Fe alloy)                     ; 8.30        ; asm 52
Inconel(Ni-Cr-Fe alloy)                        ; 8.51        ; asm 52
Indium                                         ; 7.31        ; asm 52
Indium                                         ; 7.310       ; el
Iridium                                        ; 22.15       ; sim
Iridium                                        ; 22.16       ; glo 390
Iridium                                        ; 22.4        ; aes 120
Iridium                                        ; 22.42       ; aes 117
Iridium                                        ; 22.42       ; mh 2270
Iridium                                        ; 22.420      ; el
Iridium                                        ; 22.5        ; asm 52
Iridium                                        ; 22.4        ; pht
Iron                                           ; 7.85        ; sim
Iron                                           ; 7.87        ; aes 117
Iron                                           ; 7.87        ; aes 120
Iron                                           ; 7.87        ; pht
Iron                                           ; 7.874       ; el
Iron, cast                                     ; 6.8-7.8     ; sim
Iron, cast                                     ; 7.03-7.73   ; mh 2270
Iron, cast                                     ; 7.2         ; aes 118
Iron, cast                                     ; 7.21        ; glo 390
Iron, cast gray                                ; 6.95-7.35   ; asm 52
Iron, gray cast                                ; 7.03-7.13   ; mar 6-7
Iron, ingot                                    ; 7.866       ; asm 52
Iron, liquid at melting point                  ; 7.03        ; hcp B263
Iron, malleable                                ; 7.2-7.34    ; asm 52
Iron, malleable                                ; 7.32        ; aes 118
Iron, pure                                     ; 7.874       ; asm 52
Iron, wrought                                  ; 7.77        ; glo 390
Iron, wrought                                  ; 7.80-7.90   ; mh 2270
Kovar (29% Ni, 17% Co, bal. Fe)                ; 8.36        ; hcp F159
Lanthanum                                      ; 6.145       ; el
Lanthanum                                      ; 6.166       ; aes 129
Lead                                           ; 11.34       ; mar 6-7
Lead                                           ; 11.34       ; sim
Lead                                           ; 11.342      ; mh 2270
Lead                                           ; 11.35       ; aes 117
Lead                                           ; 11.35       ; pht
Lead                                           ; 11.350      ; el
Lead 99.9%                                     ; 11.34       ; asm 52
Lead, antimonial (hard)                        ; 10.9        ; aes 118
Lead, cast                                     ; 11.35       ; glo 390
Lead, chemical                                 ; 11.35       ; aes 118
Lead, hard 4% Sb                               ; 11.04       ; asm 52
Lead, hard 6% Sb                               ; 10.88       ; asm 52
Lead, hard 8% Sb                               ; 10.74       ; asm 52
Lead, hard 9% Sb                               ; 10.66       ; asm 52
Lead, liquid at melting point                  ; 10.678      ; hcp B263
Lead, rolled                                   ; 11.39       ; glo 390
Lead, rolled                                   ; 11.39       ; sim
Lithium                                        ; .534        ; el
Lithium                                        ; 0.534       ; asm 52
Lithium                                        ; 0.534       ; pht
Lutetium                                       ; 9.835       ; aes 129
Lutetium                                       ; 9.840       ; el
Magnesium                                      ; 1.738       ; el
Magnesium                                      ; 1.738       ; sim
Magnesium                                      ; 1.74        ; aes 117
Magnesium                                      ; 1.741       ; mh 2270
Magnesium                                      ; 1.75        ; glo 390
Magnesium, liquid at melting point             ; 1.57        ; hcp B263
Manganese                                      ; 7.3         ; mh 2270
Manganese                                      ; 7.42        ; mar 6-7
Manganese                                      ; 7.43        ; asm 52
Manganese                                      ; 7.440       ; el
Manganese                                      ; 7.609       ; sim
Manganese                                      ; 7.61        ; glo 390
Manganese (3 allotropes)                       ; 7.21-7.44   ; aes 117
Mercury                                        ; 13.546      ; aes 117
Mercury                                        ; 13.546      ; asm 52
Mercury                                        ; 13.546      ; el
Mercury                                        ; 13.59       ; sim
Mercury                                        ; 13.594      ; pht
Mercury (-10 C)                                ; 13.6202     ; hcp F4
Mercury (0 C)                                  ; 13.5955     ; hcp F4
Mercury (10 C)                                 ; 13.5708     ; hcp F4
Mercury (100 C)                                ; 13.352      ; asm 1215
Mercury (100 C)                                ; 13.3522     ; hcp F4
Mercury (15 C)                                 ; 13.5585     ; hcp F4
Mercury (200 C)                                ; 13.1148     ; hcp F4
Mercury (200 C)                                ; 13.115      ; asm 1215
Mercury (25 C)                                 ; 13.5340     ; hcp F4
Mercury (30 C)                                 ; 13.5217     ; hcp F4
Mercury (300 C)                                ; 12.8806     ; hcp F4
Mercury (300 C)                                ; 12.881      ; asm 1215
Mercury (35 C)                                 ; 13.5095     ; hcp F4
Mercury (40 C)                                 ; 13.4973     ; hcp F4
Mercury (50 C)                                 ; 13.4729     ; hcp F4
Mercury (68 F)                                 ; 13.546      ; mh 2270
Mercury 20 C                                   ; 13.5462     ; hcp F4
Mercury 25 C                                   ; 13.633      ; aes 90
Mercury at 0 deg C                             ; 13.61       ; glo 390
Molybdenum                                     ; 10.19       ; glo 390
Molybdenum                                     ; 10.19       ; sim
Molybdenum                                     ; 10.2        ; mh 2270
Molybdenum                                     ; 10.22       ; aes 117
Molybdenum                                     ; 10.22       ; asm 52
Molybdenum                                     ; 10.220      ; el
Molybdenum, liquid at melting point            ; 9.33        ; hcp B263
Molydenum                                      ; 10.2        ; aes 120
Monel (Ni-Cu alloy)                            ; 8.36-8.84   ; sim
Monel (Ni-Cu alloy)                            ; 8.47        ; aes 118
Monel (Ni-Cu alloy)                            ; 8.84        ; asm 52
Monel (Ni-Cu alloy), cast                      ; 8.63        ; asm 52
Monel, rolled                                  ; 8.97        ; mar 6-7
Mu metal (high-permeability alloy)             ; 8.58        ; hcp E121
Neodymium                                      ; 7.003       ; aes 129
Neodymium                                      ; 7.007       ; el
Nichrome, 80 Ni, 20 Cr, 108 uohm-cm            ; 8.4         ; asm 52
Nickel                                         ; 8.8         ; mh 2270
Nickel                                         ; 8.8         ; sim
Nickel                                         ; 8.89        ; aes 118
Nickel                                         ; 8.9         ; aes 120
Nickel                                         ; 8.9         ; mar 6-7
Nickel                                         ; 8.9         ; pht
Nickel                                         ; 8.90        ; aes 117
Nickel                                         ; 8.902       ; el
Nickel silver                                  ; 8.4-8.9     ; sim
Nickel silver                                  ; 8.442       ; sim
Nickel silver                                  ; 8.45        ; glo 390
Nickel silver                                  ; 8.8         ; aes 118
Nickel silver, 55-18                           ; 8.70        ; asm 52
Nickel silver, 65-18                           ; 8.73        ; asm 52
Nickel, liquid at melting point                ; 7.78        ; hcp B263
Nickel, rolled                                 ; 8.666       ; sim
Nickel, rolled                                 ; 8.67        ; glo 390
Niobium                                        ; 8.57        ; aes 117
Niobium                                        ; 8.57        ; aes 120
Niobium                                        ; 8.57        ; asm 52
Niobium                                        ; 8.57        ; web
Niobium                                        ; 8.570       ; el
Osmium                                         ; 22.5        ; pht
Osmium                                         ; 22.57       ; aes 117
Osmium                                         ; 22.583      ; asm 52
Osmium                                         ; 22.590      ; el
Osmium                                         ; 22.6        ; aes 120
Palladium                                      ; 12.0        ; aes 120
Palladium                                      ; 12.02       ; asm 52
Palladium                                      ; 12.020      ; el
Permalloy 45 (high-permeability alloy)         ; 8.17        ; hcp E121
Platinum                                       ; 21.37       ; mh 2270
Platinum                                       ; 21.4        ; sim
Platinum                                       ; 21.45       ; aes 117
Platinum                                       ; 21.45       ; asm 52
Platinum                                       ; 21.45       ; pht
Platinum                                       ; 21.450      ; el
Platinum                                       ; 21.5        ; aes 120
Platinum                                       ; 21.51       ; glo 390
Platinum - 10% Rh (thermocouple material)      ; 19.97       ; asm 52
Platinum - 3.5% Rh (thermocouple material)     ; 20.9        ; asm 52
Plutonium                                      ; 19.8        ; sim
Plutonium                                      ; 19.84       ; aes 117
Plutonium                                      ; 19.84       ; asm 52
Plutonium                                      ; 19.840      ; el
Plutonium, alpha                               ; 19.86       ; pht
Potassium                                      ; .86         ; aes 117
Potassium                                      ; .862        ; el
Potassium                                      ; .870        ; mh 2270
Potassium                                      ; 0.86        ; asm 52
Praseodymium                                   ; 6.772       ; aes 129
Praseodymium                                   ; 6.773       ; el
Rhenium                                        ; 21.0        ; aes 120
Rhenium                                        ; 21.020      ; el
Rhenium                                        ; 21.04       ; asm 52
Rhodium                                        ; 12.4        ; aes 120
Rhodium                                        ; 12.41       ; aes 117
Rhodium                                        ; 12.410      ; el
Rhodium                                        ; 12.44       ; asm 52
Rubidium                                       ; 1.532       ; el
Ruthenium                                      ; 12.2        ; asm 52
Ruthenium                                      ; 12.370      ; el
Ruthenium                                      ; 12.4        ; aes 120
Samarium                                       ; 7.520       ; el
Samarium                                       ; 7.537       ; aes 129
Scandium                                       ; 2.989       ; aes 129
Scandium                                       ; 2.989       ; el
Selenium                                       ; 4.79        ; asm 52
Selenium                                       ; 4.790       ; el
Selenium                                       ; 4.8         ; aes 117
Silicon                                        ; 2.329       ; el
Silicon                                        ; 2.33        ; aes 117
Silicon                                        ; 2.33        ; asm 52
Silicon, liquid at melting point               ; 2.52        ; hcp B263
Silver                                         ; 10.42-10.53 ; mh 2270
Silver                                         ; 10.46       ; glo 390
Silver                                         ; 10.49       ; asm 52
Silver                                         ; 10.49       ; pht
Silver                                         ; 10.49       ; sim
Silver                                         ; 10.50       ; aes 117
Silver                                         ; 10.500      ; el
Silver, liquid at melting point                ; 9.33        ; hcp B263
Sodium                                         ; .97         ; aes 117
Sodium                                         ; .971        ; el
Sodium                                         ; .9712       ; mh 2270
Sodium                                         ; .977        ; sim
Sodium                                         ; .98         ; glo 390
Sodium                                         ; 0.97        ; asm 52
Sodium, liquid at melting point                ; .938        ; hcp B263
Solder, 35 Sn, 65 Pb                           ; 9.50        ; mh 2196
Solder, 50 Sn, 50 Pb                           ; 8.85        ; mh 2196
Solder, 50-50                                  ; 8.89        ; aes 118
Solder, 63 Pb, 37 Sn eutectic                  ; 8.42        ; asm 52
Solder, 63 Sn, 37 Pb eutectic                  ; 8.40        ; mh 2196
Solder, 70 Sn, 30 Pb                           ; 8.32        ; mh 2196
Steel, 304 stainless                           ; 8.02        ; aes 118
Steel, cast                                    ; 7.85        ; glo 390
Steel, low-carbon Cr-Mo                        ; 7.86        ; asm 52
Steel, plain carbon, 1020                      ; 7.86        ; aes 118
Steel, rolled                                  ; 7.85        ; sim
Steel, rolled                                  ; 7.93        ; glo 390
Steel, stainless                               ; 7.48-8.     ; sim
Steel, stainless, 17-4PH                       ; 7.8         ; asm 52
Steel, stainless, 303 & 304                    ; 7.9         ; asm 52
Steel, stainless, 316                          ; 8.0         ; asm 52
Steel, stainless, 440                          ; 7.7         ; asm 52
Steel, tool, M2 (high-speed steel)             ; 8.16        ; asm 52
Strontium                                      ; 2.540       ; el
Tantalum                                       ; 16.6        ; aes 117
Tantalum                                       ; 16.6        ; aes 120
Tantalum                                       ; 16.6        ; asm 52
Tantalum                                       ; 16.6        ; mh 2270
Tantalum                                       ; 16.654      ; el
Tellurium                                      ; 6.240       ; el
Tellurium                                      ; 6.25        ; mh 2270
Terbium                                        ; 8.229       ; el
Terbium                                        ; 8.234       ; aes 129
Thallium                                       ; 11.85       ; asm 52
Thallium                                       ; 11.850      ; el
Thorium                                        ; 11.7        ; aes 117
Thorium                                        ; 11.7        ; aes 120
Thorium                                        ; 11.72       ; asm 52
Thorium                                        ; 11.720      ; el
Thulium                                        ; 9.314       ; aes 129
Thulium                                        ; 9.321       ; el
Tin                                            ; 7.28        ; sim
Tin                                            ; 7.29        ; mh 2270
Tin                                            ; 7.31        ; aes 117
Tin (alpha)                                    ; 5.750       ; el
Tin (beta) (common form)                       ; 7.310       ; el
Tin, cast                                      ; 7.36        ; glo 390
Tin, liquid at melting point                   ; 7.0         ; hcp B263
Tin, pure                                      ; 7.3         ; asm 52
Titanium                                       ; 4.5         ; mh 2270
Titanium                                       ; 4.5         ; pht
Titanium                                       ; 4.5         ; sim
Titanium                                       ; 4.54        ; aes 117
Titanium                                       ; 4.54        ; aes 120
Titanium                                       ; 4.540       ; el
Titanium, 99.9%                                ; 4.507       ; asm 52
Titanium, commercial                           ; 5.          ; aes 118
Tungsten                                       ; 18.6-19.1   ; mh 2270
Tungsten                                       ; 19.3        ; aes 117
Tungsten                                       ; 19.3        ; aes 120
Tungsten                                       ; 19.3        ; asm 52
Tungsten                                       ; 19.3        ; pht
Tungsten                                       ; 19.300      ; el
Tungsten                                       ; 19.6        ; sim
Tungsten                                       ; 19.62       ; glo 390
Tungsten, filament                             ; 19.3        ; aes 182
Uranium                                        ; 18.7        ; mh 2270
Uranium                                        ; 18.8        ; aes 117
Uranium                                        ; 18.9        ; sim
Uranium                                        ; 18.950      ; el
Uranium                                        ; 19.05       ; pht
Uranium                                        ; 19.07       ; asm 52
Vanadium                                       ; 5.494       ; sim
Vanadium                                       ; 5.50        ; glo 390
Vanadium                                       ; 5.6         ; mh 2270
Vanadium                                       ; 6.1         ; aes 117
Vanadium                                       ; 6.1         ; aes 120
Vanadium                                       ; 6.1         ; asm 52
Vanadium                                       ; 6.110       ; el
Ytterbium                                      ; 6.965       ; el
Ytterbium                                      ; 6.972       ; aes 129
Yttrium                                        ; 4.457       ; aes 129
Yttrium                                        ; 4.469       ; el
Zinc                                           ; 7           ; aes 117
Zinc                                           ; 7.04-7.16   ; mh 2270
Zinc                                           ; 7.133       ; el
Zinc                                           ; 7.135       ; sim
Zinc                                           ; 7.14        ; aes 118
Zinc                                           ; 7.14        ; pht
Zinc, cast                                     ; 7.05        ; glo 390
Zinc, commercial rolled                        ; 7.14        ; asm 52
Zinc, liquid at melting point                  ; 6.64        ; hcp B263
Zinc, pure                                     ; 7.133       ; asm 52
Zirconium                                      ; 6.5         ; asm 52
Zirconium                                      ; 6.506       ; el
Zirconium                                      ; 6.53        ; aes 120
Zirconium, commercial                          ; 6.5         ; aes 118

category = liquid
1,1,2-Trichlorotrifluoroethane 25 C            ; 1.564       ; sim
1,2,4-Trichlorobenzene 20 C                    ; 1.454       ; sim
1,4-Dioxane 20 C                               ; 1.034       ; sim
2-Methoxyethanol 20 C                          ; .9646       ; sim
Acetic acid                                    ; 1.049       ; aes 90
Acetic acid 25 C                               ; 1.049       ; sim
Acetic acid, 100%                              ; 1.06        ; ceh 3-83
Acetic acid, 15%                               ; 1.0213      ; aes 370
Acetic acid, 30%                               ; 1.0403      ; aes 370
Acetic acid, 35%                               ; 1.0457      ; aes 370
Acetic acid, 4%                                ; 1.0058      ; aes 370
Acetic acid, 8%                                ; 1.0115      ; aes 370
Acetic acid, 90%                               ; 1.06        ; glo 390
Acetone                                        ; .787        ; aes 90
Acetone                                        ; .79         ; aes 353
Acetone                                        ; 0.79        ; pht
Acetone 25 C                                   ; .7846       ; sim
Acetonitrile 20 C                              ; .7822       ; sim
Acid, acetic (CH3COOH)                         ; 1.05        ; pht
Acid, sulfuric (H2SO4)                         ; 1.39        ; pht
Air (liquid, bp = 79 K)                        ; .875        ; aes 97
Alcohol, butyl                                 ; .81         ; aes 353
Alcohol, denatured (methanol)                  ; .79         ; aes 353
Alcohol, ethyl                                 ; .787        ; aes 90
Alcohol, ethyl                                 ; .789        ; glo 390
Alcohol, ethyl                                 ; .789        ; mar 6-7
Alcohol, ethyl (grain)                         ; 0.7892      ; pht
Alcohol, ethyl 25 C                            ; .7851       ; sim
Alcohol, isopropyl (2-propanol)                ; .79         ; aes 353
Alcohol, isopropyl (rubbing)                   ; 0.7854      ; pht
Alcohol, methyl                                ; .789        ; aes 90
Alcohol, methyl                                ; .791        ; glo 390
Alcohol, methyl                                ; .796        ; mar 6-7
Alcohol, methyl (methanol)                     ; .79         ; aes 353
Alcohol, methyl (wood)                         ; 0.7913      ; pht
Alcohol, methyl 25 C                           ; .7865       ; sim
Alcohol, propyl                                ; .802        ; aes 90
Alcohol, propyl 25 C                           ; .8          ; sim
Alcohol, wood (methanol)                       ; .79         ; aes 353
Ammonia                                        ; 0.771       ; pht
Ammonia (aqua) 25 C                            ; .8234       ; sim
Amyl acetate (banana oil)                      ; .88         ; aes 353
Analine 25 C                                   ; 1.019       ; sim
Argon (liquid, bp = 87 K)                      ; 1.403       ; aes 97
Automobile oils 15 C                           ; .88-.94     ; sim
Beer (varies) 10 C                             ; 1.01        ; sim
Beer, pilsner, 4 C                             ; 1.008       ; pht
Benzene                                        ; .876        ; aes 90
Benzene                                        ; 0.87        ; pht
Benzene 25 C                                   ; .8738       ; sim
Benzil 25 C                                    ; 1.08        ; sim
Blood                                          ; 1.035       ; pht
Bromine 25 C                                   ; 3.12        ; sim
Butane                                         ; 0.551       ; pht
Butane 25 C                                    ; .5991       ; sim
Butyric acid 20 C                              ; .959        ; sim
Caproic acid 25 C                              ; .9211       ; sim
Carbolic acid 15 C                             ; .9563       ; sim
Carbon disulfide                               ; 1.265       ; aes 90
Carbon disulfide 25 C                          ; 1.261       ; sim
Carbon tetrachloride                           ; 1.59        ; aes 90
Carbon tetrachloride 25 C                      ; 1.584       ; sim
Carene 25 C                                    ; .857        ; sim
Castor oil                                     ; .96         ; aes 90
Castor oil 25 C                                ; .9561       ; sim
Chloride 25 C                                  ; 1.56        ; sim
Chlorobenzene 20 C                             ; 1.106       ; sim
Chloroform                                     ; 1.47        ; aes 90
Chloroform                                     ; 1.500       ; mar 6-7
Chloroform                                     ; 1.52        ; glo 390
Chloroform                                     ; 1.522       ; sim
Chloroform 20 C                                ; 1.489       ; sim
Chloroform 25 C                                ; 1.465       ; sim
Citric acid 25 C                               ; 1.66        ; sim
Coconut oil 15 C                               ; .9243       ; sim
Corn syrup                                     ; 1.38        ; pht
Cotton seed oil 15 C                           ; .9259       ; sim
Creosote 15 C                                  ; 1.067       ; sim
Cresol 25 C                                    ; 1.024       ; sim
Crude oil                                      ; .76-.85     ; hep 43
Crude oil, 32.6 deg API 60 F                   ; .862        ; sim
Crude oil, 35.6 deg API 60 F                   ; .847        ; sim
Crude oil, 40 deg API 60 F                     ; .825        ; sim
Crude oil, 48 deg API 60 F                     ; .79         ; sim
Crude oil, California 60 F                     ; .915        ; sim
Crude oil, Mexican 60 F                        ; .973        ; sim
Crude oil, Texas 60 F                          ; .873        ; sim
Cumene 25 C                                    ; .8602       ; sim
Cyclohexane 20 C                               ; .7785       ; sim
Cyclopentane 20 C                              ; .7454       ; sim
Decane                                         ; .728        ; aes 90
Decane 25 C                                    ; .7263       ; sim
Dichloromethane 20 C                           ; 1.326       ; sim
Diesel                                         ; 0.8         ; pht
Diesel fuel oil 20 to 60 15 C                  ; .82-.95     ; sim
Diesel oil, #1                                 ; .875        ; aes 389
Diesel oil, #2                                 ; .920        ; aes 389
Diesel oil, #4                                 ; .960        ; aes 389
Diethyl ether 20 C                             ; .714        ; sim
Diethylene glycol 15 C                         ; 1.12        ; sim
Dimethyl acetamide 20 C                        ; .9415       ; sim
Dimethyl sulfoxide 20 C                        ; 1.1         ; sim
Dodecane 25 C                                  ; .7546       ; sim
Ethane (liquid, bp = 185 K)                    ; .548        ; aes 97
Ethane -89 C                                   ; .5703       ; sim
Ether                                          ; .715        ; aes 90
Ether                                          ; .736        ; mar 6-7
Ether                                          ; .737        ; sim
Ether                                          ; .74         ; glo 390
Ethyl acetate 20 C                             ; .9006       ; sim
Ethyl alcohol 20 C                             ; .7892       ; sim
Ethyl ether 20 C                               ; .7133       ; sim
Ethylamine 16 C                                ; .6808       ; sim
Ethylene dichloride 20 C                       ; 1.253       ; sim
Ethylene glycol                                ; 1.100       ; aes 90
Ethylene glycol 25 C                           ; 1.097       ; sim
Fish oil                                       ; .93         ; aes 353
Fluorine (liquid, bp = 85 K)                   ; 1.50        ; aes 97
Fluorine refrigerant R-12 25 C                 ; 1.311       ; sim
Formaldehyde                                   ; 1.13        ; pht
Formaldehyde 45 C                              ; .8121       ; sim
Formic acid 10% concentration 20 C             ; 1.025       ; sim
Formic acid 80% concentration 20 C             ; 1.221       ; sim
Freon - 11 21 C                                ; 1.49        ; sim
Freon - 21 21 C                                ; 1.37        ; sim
Freon 12, liquid                               ; 1.311       ; pht
Fuel oil 60 F                                  ; .8901       ; sim
Furan 25 C                                     ; 1.416       ; sim
Furforol 25 C                                  ; 1.155       ; sim
Gas oils 60 F                                  ; .89         ; sim
Gasoline                                       ; .68-.72     ; hep 43
Gasoline                                       ; .71-.77     ; wp
Gasoline                                       ; 0.803       ; pht
Gasoline, natural 60 F                         ; .7112       ; sim
Gasoline, vehicle 60 F                         ; .7372       ; sim
Glucose 60 F                                   ; 1.35-1.44   ; sim
Glycerin 25 C                                  ; 1.259       ; sim
Glycerine                                      ; 1.26        ; hep 43
Glycerine                                      ; 1.26        ; pht
Glycerol 25 C                                  ; 1.126       ; sim
Glyme 20 C                                     ; .8691       ; sim
Helium 3 (liquid, bp = 3.2 K)                  ; .0589       ; aes 97
Helium 4 (liquid, bp = 4.215 K)                ; .125        ; aes 97
Helium, liquid, 4 K                            ; 0.147       ; pht
Heptane 25 C                                   ; .6795       ; sim
Hexane 25 C                                    ; .6548       ; sim
Hexanol 25 C                                   ; .8105       ; sim
Hexene 25 C                                    ; .6712       ; sim
Honey                                          ; 1.42        ; pht
Hydrazine 25 C                                 ; .7945       ; sim
Hydrochloric acid 40%                          ; 1.201       ; sim
Hydrochloric acid, 15%                         ; 1.0746      ; aes 370
Hydrochloric acid, 30%                         ; 1.1510      ; aes 370
Hydrochloric acid, 35%                         ; 1.1759      ; aes 370
Hydrochloric acid, 4%                          ; 1.0198      ; aes 370
Hydrochloric acid, 40%                         ; 1.2         ; glo 390
Hydrochloric acid, 40%                         ; 1.2         ; mar 6-7
Hydrochloric acid, 8%                          ; 1.0395      ; aes 370
Hydrogen (H2), liquid, 17 K                    ; 0.071       ; pht
Hydrogen (liquid, bp = 20 K)                   ; .071        ; aes 97
Iodine 25 C                                    ; 4.927       ; sim
Ionene 25 C                                    ; .9323       ; sim
Iso-octane 20 C                                ; .6919       ; sim
Isobutyl alcohol 20 C                          ; .8016       ; sim
Isopropyl alcohol 20 C                         ; .7854       ; sim
Isopropyl myristate 20 C                       ; .8532       ; sim
Kerosene                                       ; .78-.82     ; mar 6-7
Kerosene                                       ; .823        ; aes 90
Kerosene                                       ; .825        ; aes 389
Kerosene                                       ; 0.81        ; pht
Kerosene 60 F                                  ; .8171       ; sim
Linolenic acid 25 C                            ; .8986       ; sim
Linseed (flax) oil, boiled                     ; .95         ; aes 353
Linseed (flax) oil, brown                      ; .97         ; aes 353
Linseed (flax) oil, raw                        ; .93         ; aes 353
Linseed oil                                    ; .93         ; aes 90
Linseed oil 25 C                               ; .9291       ; sim
Lye, 66% solution in water                     ; 1.70        ; mar 6-7
Machine oil                                    ; .9          ; hep 43
Methane (liquid, bp = 111 K)                   ; .424        ; aes 97
Methane -164 C                                 ; .4645       ; sim
Methane, liquid, -90 C                         ; 0.162       ; pht
Methanol 20 C                                  ; .7913       ; sim
Methyl ethyl ketone (MEK) 20 C                 ; .8049       ; sim
Methyl ethyl ketone (MEK) 25 C                 ; .8025       ; sim
Methyl isoamyl ketone 20 C                     ; .888        ; sim
Methyl isobutyl ketone 20 C                    ; .8008       ; sim
Methyl n-propyl ketone 20 C                    ; .8082       ; sim
Methyl t-butyl ether 20 C                      ; .7405       ; sim
Milk 15 C                                      ; 1.02-1.05   ; sim
Milk of average fat content                    ; 1.03        ; hep 43
Milk, cow, heavy cream                         ; 0.994       ; pht
Milk, cow, light cream                         ; 1.012       ; pht
Milk, cow, skim                                ; 1.033       ; pht
Milk, cow, whole                               ; 1.03        ; pht
Mineral spirits (Stoddard solvent)             ; .66         ; aes 353
N,N-Dimethylformamide 20 C                     ; .9487       ; sim
N-Methylpyrrolidone 20 C                       ; 1.03        ; sim
NaCl in water (salt brine), 15%                ; 1.1105      ; aes 370
NaCl in water (salt brine), 25%                ; 1.1909      ; aes 370
NaCl in water (salt brine), 4%                 ; 1.0286      ; aes 370
NaCl in water (salt brine), 8%                 ; 1.0578      ; aes 370
NaCl in water 20 C (salt brine), 0.5%          ; 1.0036      ; hcp D299
NaCl in water 20 C (salt brine), 1%            ; 1.0071      ; hcp D299
NaCl in water 20 C (salt brine), 10%           ; 1.0726      ; hcp D300
NaCl in water 20 C (salt brine), 11%           ; 1.0801      ; hcp D300
NaCl in water 20 C (salt brine), 12%           ; 1.0876      ; hcp D300
NaCl in water 20 C (salt brine), 13%           ; 1.0952      ; hcp D300
NaCl in water 20 C (salt brine), 14%           ; 1.1028      ; hcp D300
NaCl in water 20 C (salt brine), 15%           ; 1.1105      ; hcp D300
NaCl in water 20 C (salt brine), 16%           ; 1.1182      ; hcp D300
NaCl in water 20 C (salt brine), 17%           ; 1.1260      ; hcp D300
NaCl in water 20 C (salt brine), 18%           ; 1.1339      ; hcp D300
NaCl in water 20 C (salt brine), 19%           ; 1.1418      ; hcp D300
NaCl in water 20 C (salt brine), 2%            ; 1.0143      ; hcp D299
NaCl in water 20 C (salt brine), 20%           ; 1.1498      ; hcp D300
NaCl in water 20 C (salt brine), 21%           ; 1.1579      ; hcp D300
NaCl in water 20 C (salt brine), 22%           ; 1.1660      ; hcp D300
NaCl in water 20 C (salt brine), 23%           ; 1.1742      ; hcp D300
NaCl in water 20 C (salt brine), 24%           ; 1.1825      ; hcp D300
NaCl in water 20 C (salt brine), 25%           ; 1.1909      ; hcp D300
NaCl in water 20 C (salt brine), 26%           ; 1.1993      ; hcp D300
NaCl in water 20 C (salt brine), 3%            ; 1.0214      ; hcp D299
NaCl in water 20 C (salt brine), 4%            ; 1.0286      ; hcp D300
NaCl in water 20 C (salt brine), 5%            ; 1.0358      ; hcp D300
NaCl in water 20 C (salt brine), 6%            ; 1.0431      ; hcp D300
NaCl in water 20 C (salt brine), 7%            ; 1.0504      ; hcp D300
NaCl in water 20 C (salt brine), 8%            ; 1.0578      ; hcp D300
NaCl in water 20 C (salt brine), 9%            ; 1.0651      ; hcp D300
Naphtha 15 C (lighter fluid, camp stove fuel)  ; .6648       ; sim
Naphtha, wood 25 C                             ; .9595       ; sim
Naptha, aromatic (lighter fluid)               ; .85         ; aes 353
Napthalene 25 C                                ; .8201       ; sim
Neon (liquid, bp = 111 K)                      ; 1.205       ; aes 97
Nitric acid, 15%                               ; 1.0861      ; aes 370
Nitric acid, 30%                               ; 1.1822      ; aes 370
Nitric acid, 35%                               ; 1.2158      ; aes 370
Nitric acid, 4%                                ; 1.0219      ; aes 370
Nitric acid, 8%                                ; 1.0446      ; aes 370
Nitric acid, 91%                               ; 1.5         ; mar 6-7
Nitric acid, 91%                               ; 1.506       ; sim
Nitric acid, 91%                               ; 1.51        ; glo 390
Nitrobenzene                                   ; 1.2         ; hep 43
Nitrogen (liquid, bp = 77.4 K)                 ; .810        ; aes 97
Nitrogen, liquid, 74 K                         ; 0.808       ; pht
Ocimene 25 C                                   ; .7977       ; sim
Octane                                         ; .701        ; aes 90
Octane 15 C                                    ; .9179       ; sim
Oil, SAE10W, 15 deg C                          ; 0.870       ; aes 624
Oil, SAE10W-30, 15 deg C                       ; 0.876       ; aes 624
Oil, SAE30, 15 deg C                           ; 0.891       ; aes 624
Oil, gear, SAE90, 15 deg C                     ; 0.930       ; aes 624
Oil, linseed                                   ; .94         ; glo 390
Oil, linseed                                   ; .942        ; sim
Oil, mineral, lubricant                        ; .88-.94     ; mar 6-7
Oil, petroleum                                 ; .88         ; glo 390
Oil, petroleum                                 ; .881        ; sim
Oil, transmission, 15 deg C                    ; 0.887       ; aes 624
Oil, vegetable                                 ; .91-.94     ; mar 6-7
Oil, vegetable, coconut                        ; 0.924       ; pht
Oil, vegetable, corn                           ; 0.922       ; pht
Oil, vegetable, olive                          ; 0.918       ; pht
Oil, vegetable, palm                           ; 0.915       ; pht
Oil, vegetable, peanut                         ; 0.914       ; pht
Oil, vegetable, soya                           ; 0.927       ; pht
Olive oil 20 C                                 ; .8-.92      ; sim
Oxygen (liquid) -183 C                         ; 1.14        ; sim
Oxygen, liquid, 87 K                           ; 1.155       ; pht
Palmitic acid 25 C                             ; .8506       ; sim
Pentane 20 C                                   ; .6262       ; sim
Pentane 25 C                                   ; .6248       ; sim
Perchlorethylene                               ; 1.6         ; pht
Petroleum                                      ; .87         ; mar 6-7
Petroleum ether 20 C                           ; .64         ; sim
Phenol 25 C                                    ; 1.072       ; sim
Phosgene 0 C                                   ; 1.378       ; sim
Phytadiene 25 C                                ; .8234       ; sim
Pinene 25 C                                    ; .857        ; sim
Pitch                                          ; 1.07        ; aes 178
Pitch                                          ; 1.07-1.15   ; mar 6-7
Pitch                                          ; 1.15        ; glo 390
Pitch                                          ; 1.153       ; sim
Propane (liquid)                               ; .495        ; aes 90
Propane (liquid, bp = 231 K)                   ; .582        ; aes 97
Propane -40 C                                  ; .5831       ; sim
Propane, R-290 25 C                            ; .4935       ; sim
Propanol 25 C                                  ; .8041       ; sim
Propylene (liquid)                             ; .514        ; aes 90
Propylene (liquid, bp = 225 K)                 ; .614        ; aes 97
Propylene 25 C                                 ; .5144       ; sim
Propylene carbonate 20 C                       ; 1.201       ; sim
Propylene glycol                               ; .968        ; aes 90
Propylene glycol 25 C                          ; .9653       ; sim
Pyridine 25 C                                  ; .9787       ; sim
Pyrrole 25 C                                   ; .9659       ; sim
Rape seed oil 20 C                             ; .92         ; sim
Resorcinol 25 C                                ; 1.269       ; sim
Rosin oil 15 C                                 ; .98         ; sim
Sabiname 25 C                                  ; .8121       ; sim
Sea water                                      ; 1.03        ; aes 90
Sea water 25 C                                 ; 1.025       ; sim
Seawater                                       ; 1.03        ; aes 90
Sewage, sludge                                 ; .72         ; glo 390
Silane 25 C                                    ; .7176       ; sim
Silicone                                       ; 0.993       ; pht
Sodium hydroxide (caustic soda) 15 C           ; 1.25        ; sim
Sorbaldehyde 25 C                              ; .8954       ; sim
Soya bean oil 15 C                             ; .924-.928   ; sim
Soybean oil                                    ; .93         ; aes 353
Stearic acid 25 C                              ; .8906       ; sim
Styrene 25 C                                   ; .9034       ; sim
Sugar solution 68 Brix 15 C                    ; 1.338       ; sim
Sulfuric acid 100% conc.                       ; 1.839       ; hcp F8
Sulfuric acid 95% conc. 20 C                   ; 1.839       ; sim
Sulfuric acid, 15%                             ; 1.1039      ; aes 370
Sulfuric acid, 30%                             ; 1.2206      ; aes 370
Sulfuric acid, 35%                             ; 1.2620      ; aes 370
Sulfuric acid, 4%                              ; 1.0269      ; aes 370
Sulfuric acid, 8%                              ; 1.0540      ; aes 370
Sulfuric acid, 87%                             ; 1.79        ; glo 390
Sulfuric acid, 87%                             ; 1.8         ; mar 6-7
Sunflower oil  20 C                            ; .92         ; sim
Tar                                            ; 1.02        ; aes 178
Tar                                            ; 1.15        ; glo 390
Terpinene 25 C                                 ; .8474       ; sim
Tetrahydrofuran 20 C                           ; .888        ; sim
Tobacco seed oil                               ; .92         ; aes 353
Toluene (toluol)                               ; .865        ; aes 90
Toluene (toluol)                               ; .87         ; aes 353
Toluene (toluol) 20 C                          ; .8669       ; sim
Toluene (toluol) 25 C                          ; .8623       ; sim
Trichloroethylene                              ; 1.46        ; aes 353
Triethylamine 20 C                             ; .7276       ; sim
Trifluoroacetic acid 20 C                      ; 1.489       ; sim
Tung oil                                       ; .94         ; aes 353
Turpentine                                     ; .85         ; aes 353
Turpentine                                     ; .865        ; sim
Turpentine                                     ; .87         ; aes 90
Turpentine                                     ; .87         ; glo 390
Turpentine 25 C                                ; .8682       ; sim
Water (4 C)                                    ; 1.00        ; aes 90
Water (4 C)                                    ; 1.00        ; glo 390
Water, (0 C & 1 atm)                           ; 0.9999      ; aes 89
Water, (10 C & 1 atm)                          ; .9997       ; aes 89
Water, (100 C & 1 atm)                         ; .9584       ; aes 89
Water, (15 C & 1 atm)                          ; .9992       ; aes 89
Water, (20 C & 1 atm)                          ; .9982       ; aes 89
Water, (25 C & 1 atm)                          ; .9970       ; aes 89
Water, (30 C & 1 atm)                          ; .9957       ; aes 89
Water, (35 C & 1 atm)                          ; .9941       ; aes 89
Water, (40 C & 1 atm)                          ; .9922       ; aes 89
Water, (45 C & 1 atm)                          ; .9903       ; aes 89
Water, (5 C & 1 atm)                           ; 1.0000      ; aes 89
Water, (50 C & 1 atm)                          ; .9881       ; aes 89
Water, (55 C & 1 atm)                          ; .9857       ; aes 89
Water, (60 C & 1 atm)                          ; .9832       ; aes 89
Water, (65 C & 1 atm)                          ; .9806       ; aes 89
Water, (70 C & 1 atm)                          ; .9778       ; aes 89
Water, (75 C & 1 atm)                          ; .9749       ; aes 89
Water, (80 C & 1 atm)                          ; .9718       ; aes 89
Water, (85 C & 1 atm)                          ; .9687       ; aes 89
Water, (90 C & 1 atm)                          ; .9653       ; aes 89
Water, (95 C & 1 atm)                          ; .9619       ; aes 89
Water, heavy (deuterium oxide)                 ; 1.1086      ; hep 43
Water, ice                                     ; .88-.92     ; mar 6-7
Water, liquid, 0 C                             ; 0.99984     ; pht
Water, liquid, 10 C                            ; 0.9997      ; pht
Water, liquid, 100 C                           ; 0.9584      ; pht
Water, liquid, 20 C                            ; 0.99821     ; pht
Water, liquid, 30 C                            ; 0.99565     ; pht
Water, liquid, 4 C                             ; 0.99998     ; pht
Water, liquid, 50 C                            ; 0.98803     ; pht
Water, pure                                    ; 1.          ; sim
Water, pure 4 C                                ; 1.          ; sim
Water, saline (0.9 % NaCl)                     ; 1.004       ; pht
Water, saturated (0 C & 0.00603 atm)           ; .9998       ; aes 18
Water, saturated (100 C & 1 atm)               ; .9581       ; aes 18
Water, saturated (20 C & 0.023 atm)            ; .9983       ; aes 18
Water, saturated (50 C & 0.123 atm)            ; .9880       ; aes 18
Water, sea                                     ; 1.025       ; pht
Water, sea                                     ; 1.026       ; sim
Water, sea                                     ; 1.03        ; aes 90
Water, sea                                     ; 1.03        ; glo 390
Water, sea 77 F                                ; 1.022       ; sim
Water, tap, 20 C                               ; .9982       ; web
Whale oil 15 C                                 ; .925        ; sim
Xylene                                         ; .89         ; aes 353
Xylene (ortho) 20 C                            ; .8802       ; sim
n-Butyl acetate 20 C                           ; .8796       ; sim
n-Butyl alcohol 20 C                           ; .8097       ; sim
n-Butyl chloride 20 C                          ; .8862       ; sim
n-Propyl alcohol 20 C                          ; .8037       ; sim
o-Dichlorobenzene 20 C                         ; 1.306       ; sim

category = misc
Aerogel, silica                                ; .11         ; aes 177
Alabaster, carbonate                           ; 2.69-2.78   ; aes 178
Alabaster, sulfate                             ; 2.26-2.32   ; aes 178
Alfalfa, ground                                ; .256        ; sim
Alfalfa, ground                                ; .26         ; glo 390
Alum, lumpy                                    ; .88         ; glo 390
Alum, lumpy                                    ; .881        ; sim
Alum, pulverized                               ; .753        ; sim
Amatol 50-50 (explosive)                       ; 1.5         ; aes 399
Amatol 80-20 (explosive)                       ; 1.4         ; aes 399
Amber                                          ; 1.06-1.11   ; aes 178
Ammonium nitrate                               ; .73         ; sim
Ammonium sulfate                               ; .83         ; glo 390
Ammonium sulphate, dry                         ; 1.13        ; sim
Ammonium sulphate, wet                         ; 1.29        ; sim
Aniline                                        ; 1.02        ; hep 43
Apples                                         ; .64         ; glo 390
Apples                                         ; .641        ; sim
Arsenic                                        ; 5.67        ; glo 390
Arsenic                                        ; 5.671       ; sim
Asbestos                                       ; 2.0-2.8     ; aes 178
Asbestos millboard                             ; 1.0         ; aes 177
Asbestos rock                                  ; 1.6         ; sim
Asbestos slate                                 ; 1.8         ; aes 178
Asbestos, cement board                         ; 1.4         ; aes 177
Asbestos, shredded                             ; .32-.4      ; sim
Asbestos, shredded                             ; .35         ; glo 390
Asbestos, solid                                ; 2.45        ; glo 390
Ashes                                          ; .66         ; glo 390
Ashes, dry                                     ; .57-.65     ; sim
Ashes, wet                                     ; .73-.89     ; sim
Asphalt                                        ; 1.1         ; aes 177
Asphalt                                        ; 1.1-1.5     ; aes 178
Asphalt, crushed                               ; .72         ; glo 390
Asphalt, crushed                               ; .721        ; sim
Bagasse (sugar cane fiber)                     ; .12         ; sim
Baking powder                                  ; .72         ; glo 390
Baking powder                                  ; .721        ; sim
Balsam wool (chemically-treated wood fiber)    ; .035        ; hcp E5
Barley                                         ; .609        ; sim
Barley                                         ; .61         ; glo 390
Barley, bulk                                   ; .62         ; mar 6-7
Basalt                                         ; 2.4-3.1     ; aes 178
Beans, castor                                  ; .577        ; sim
Beans, castor                                  ; .58         ; glo 390
Beans, cocoa                                   ; .59         ; glo 390
Beans, cocoa                                   ; .593        ; sim
Beans, navy                                    ; .8          ; glo 390
Beans, navy                                    ; .801        ; sim
Beans, soy                                     ; .72         ; glo 390
Beans, soy                                     ; .721        ; sim
Beeswax                                        ; .95         ; aes 177
Beeswax                                        ; .96         ; glo 390
Beeswax                                        ; .96-.97     ; aes 178
Beeswax                                        ; .961        ; sim
Beets                                          ; .72         ; glo 390
Beets                                          ; .721        ; sim
Bicarbonate of soda (NaHCO3)                   ; .689        ; sim
Bicarbonate of soda (NaHCO3)                   ; .69         ; glo 390
Black powder (KNO3, charcoal, S)               ; 1.74        ; aes 399
Blood                                          ; 1.06        ; web
Body fat                                       ; 0.918       ; pht
Bone                                           ; 1.7-2.0     ; aes 178
Bone                                           ; 1.9         ; pht
Bones, pulverized                              ; .88         ; glo 390
Bones, pulverized                              ; .881        ; sim
Boron fiber                                    ; 2.3         ; aes 182
Bran                                           ; .256        ; sim
Bran                                           ; .26         ; glo 390
Brewers grain                                  ; .43         ; glo 390
Brewers grain                                  ; .432        ; sim
Brick                                          ; 1.4-2.2     ; aes 178
Brick, chrome                                  ; 2.803       ; sim
Brick, common                                  ; 1.75        ; aes 177
Brick, common red                              ; 1.92        ; glo 390
Brick, common red                              ; 1.922       ; sim
Brick, fire clay                               ; 2.40        ; glo 390
Brick, fire clay                               ; 2.403       ; sim
Brick, hard                                    ; 1.8-2.3     ; mar 6-7
Brick, hard                                    ; 2.0         ; aes 177
Brick, magnesia                                ; 2.563       ; sim
Brick, medium                                  ; 1.5-2       ; mar 6-7
Brick, silica                                  ; 2.05        ; sim
Brick, soft                                    ; 1.4-1.9     ; mar 6-7
Broadcloth                                     ; .25         ; hep 45
Buckwheat                                      ; .657        ; sim
Buckwheat                                      ; .66         ; glo 390
Bullseye smokeless powder                      ; .4          ; aes 399
Butter                                         ; .86-.87     ; aes 178
Butter                                         ; .865        ; sim
Butter                                         ; .87         ; glo 390
Butter                                         ; 0.911       ; pht
Calamime                                       ; 4.1-4.5     ; aes 178
Calcium carbide (CaC2)                         ; 1.20        ; glo 390
Calcium carbide (CaC2)                         ; 1.201       ; sim
Calcium carbide (CaC2)                         ; 2.22        ; aes 183
Camel hair                                     ; 1.32        ; aes 172
Camphor                                        ; .99         ; aes 178
Carbon                                         ; 2.25        ; pht
Carbon dioxide, solid (sublimes at 195 K)      ; 1.56        ; aes 97
Carbon, porous                                 ; 1.04        ; aes 180
Carbon, powdered                               ; .08         ; glo 390
Carbon, powdered                               ; .08         ; sim
Carbon, refractory brick                       ; 1.63        ; aes 180
Carbon, solid                                  ; 2.146       ; sim
Carbon, solid                                  ; 2.15        ; glo 390
Cardboard                                      ; .689        ; sim
Cardboard                                      ; .69         ; aes 178
Cardboard                                      ; .69         ; glo 390
Celluloid                                      ; 1.4         ; aes 178
Celotex (sugar cane fiber)                     ; .21-.24     ; hcp E5
Cement - clinker                               ; 1.29-1.54   ; sim
Cement, Portland                               ; 1.505       ; sim
Cement, Portland                               ; 1.506       ; sim
Cement, Portland                               ; 1.6         ; glo 390
Cement, Portland                               ; 3.1-3.2     ; mar 6-7
Cement, mortar                                 ; 2.16        ; glo 390
Cement, mortar                                 ; 2.162       ; sim
Cement, set                                    ; 2.7-3.0     ; aes 178
Cement, slurry                                 ; 1.44        ; glo 390
Cement, slurry                                 ; 1.442       ; sim
Cement, stone and sand                         ; 2.2-2.4     ; mar 6-7
Charcoal                                       ; .208        ; sim
Charcoal                                       ; .21         ; glo 390
Charcoal, oak                                  ; .57         ; aes 178
Charcoal, pine                                 ; .28-.44     ; aes 178
Charcoal, wood                                 ; .4          ; aes 177
Chocolate, powder                              ; .64         ; glo 390
Chocolate, powder                              ; .641        ; sim
Chrome carbide (Cr3C2)                         ; 6.7         ; aes 183
Chrome carbide (Cr7C3)                         ; 6.92        ; aes 183
Chromic acid, flake                            ; 1.201       ; sim
Cinders, Coal, ash                             ; .641        ; sim
Cinders, coal, ash                             ; .64         ; glo 390
Cinders, furnace                               ; .91         ; glo 390
Cinders, furnace                               ; .913        ; sim
Clay                                           ; 1.8-2.6     ; aes 178
Clay and gravel, dry                           ; 1.6         ; mar 6-7
Clay, compacted                                ; 1.746       ; sim
Clay, compacted                                ; 1.75        ; glo 390
Clay, damp, plastic                            ; 1.76        ; mar 6-7
Clay, dry                                      ; 1           ; mar 6-7
Clay, dry excavated                            ; 1.089       ; sim
Clay, dry excavated                            ; 1.09        ; glo 390
Clay, dry lump                                 ; 1.07        ; glo 390
Clay, dry lump                                 ; 1.073       ; sim
Clay, fire                                     ; 1.36        ; glo 390
Clay, fire                                     ; 1.362       ; sim
Clay, wet excavated                            ; 1.826       ; sim
Clay, wet excavated                            ; 1.83        ; glo 390
Clay, wet lump                                 ; 1.60        ; glo 390
Clay, wet lump                                 ; 1.602       ; sim
Clover seed                                    ; .769        ; sim
Clover seed                                    ; .77         ; glo 390
Coal, anthracite                               ; 1.4-1.8     ; aes 178
Coal, anthracite                               ; 1.5         ; aes 177
Coal, anthracite, broken                       ; 1.11        ; glo 390
Coal, anthracite, solid                        ; 1.51        ; glo 390
Coal, bituminous                               ; 1.2         ; aes 177
Coal, bituminous                               ; 1.2-1.5     ; aes 178
Coal, bituminous, broken                       ; .83         ; glo 390
Coal, bituminous, solid                        ; 1.35        ; glo 390
Cocoa butter                                   ; .89-.91     ; aes 178
Coconut, meal                                  ; .51         ; glo 390
Coconut, meal                                  ; .513        ; sim
Coconut, shredded                              ; .35         ; glo 390
Coconut, shredded                              ; .352        ; sim
Coffee beans, fresh                            ; .56         ; glo 390
Coffee beans, roasted                          ; .43         ; glo 390
Coffee, fresh beans                            ; .561        ; sim
Coffee, roast beans                            ; .432        ; sim
Coke                                           ; .42         ; glo 390
Coke                                           ; .57-.65     ; sim
Coke                                           ; 1.0-1.7     ; aes 178
Concrete, dry                                  ; 1.6         ; hep 45
Concrete, gravel                               ; 2.40        ; glo 390
Concrete, gravel                               ; 2.403       ; sim
Concrete, light                                ; 1.4         ; aes 177
Concrete, limestone w/ Portland cement         ; 2.37        ; glo 390
Concrete, reinforced, 8% moist. by wt          ; 2.2         ; hep 45
Concrete, stone                                ; 2.2         ; aes 177
Concrete, w/crushed rock, 8% moist. by wt      ; 2.0         ; hep 45
Copper sulfate, ground                         ; 3.604       ; sim
Copper sulphate, ground                        ; 3.6         ; glo 390
Copra, expeller cake chopped (dried coconut)   ; .465        ; sim
Copra, expeller cake ground (dried coconut)    ; .513        ; sim
Copra, meal, ground (dried coconut)            ; .641        ; sim
Copra, medium size (dried coconut)             ; .529        ; sim
Cork                                           ; .22-.26     ; aes 178
Cork                                           ; .22-.26     ; mar 6-7
Cork linoleum                                  ; .54         ; aes 178
Cork, ground                                   ; .16         ; glo 390
Cork, ground                                   ; .16         ; sim
Cork, solid                                    ; .24         ; glo 390
Cork, solid                                    ; .24         ; sim
Corkboard                                      ; .2          ; aes 177
Corn or rye, bulk                              ; .73         ; mar 6-7
Corn starch, loosely packed                    ; 0.54        ; pht
Corn starch, tightly packed                    ; 0.630       ; pht
Corn, grits                                    ; .67         ; glo 390
Corn, grits                                    ; .673        ; sim
Corn, on the cob                               ; .72         ; glo 390
Corn, on the cob                               ; .721        ; sim
Corn, shelled                                  ; .72         ; glo 390
Corn, shelled                                  ; .721        ; sim
Cotton                                         ; 1.54        ; aes 172
Cotton, flax, hemp                             ; 1.47-1.5    ; mar 6-7
Cottonseed, cake, lumpy                        ; .673        ; sim
Cottonseed, dry, de-linted                     ; .561        ; sim
Cottonseed, dry, delinted                      ; .56         ; glo 390
Cottonseed, dry, not de-linted                 ; .32         ; sim
Cottonseed, dry, not delinted                  ; .32         ; glo 390
Cottonseed, hulls                              ; .19         ; glo 390
Cottonseed, hulls                              ; .192        ; sim
Cottonseed, meal                               ; .59         ; glo 390
Cottonseed, meal                               ; .593        ; sim
Cottonseed, meats                              ; .64         ; glo 390
Cottonseed, meats                              ; .641        ; sim
Cottonwood                                     ; .416        ; sim
Earth (dirt), dense                            ; 2.0         ; glo 390
Earth (dirt), dense                            ; 2.002       ; sim
Earth (dirt), dry                              ; 1.4         ; aes 177
Earth (dirt), dry, loose                       ; 1.2         ; mar 6-7
Earth (dirt), dry, packed                      ; 1.5         ; mar 6-7
Earth (dirt), loam, dry, excavated             ; 1.249       ; sim
Earth (dirt), loam, dry, excavated             ; 1.25        ; glo 390
Earth (dirt), moist, excavated                 ; 1.44        ; glo 390
Earth (dirt), moist, excavated                 ; 1.442       ; sim
Earth (dirt), moist, loose                     ; 1.3         ; mar 6-7
Earth (dirt), moist, packed                    ; 1.6         ; mar 6-7
Earth (dirt), mud, flowing                     ; 1.7         ; mar 6-7
Earth (dirt), mud, packed                      ; 1.8         ; mar 6-7
Earth (dirt), packed                           ; 1.52        ; glo 390
Earth (dirt), packed                           ; 1.522       ; sim
Earth (dirt), soft loose mud                   ; 1.73        ; sim
Earth (dirt), soft, loose mud                  ; 1.73        ; glo 390
Earth (dirt), wet, excavated                   ; 1.60        ; glo 390
Earth (dirt), wet, excavated                   ; 1.602       ; sim
Earth, Fullers, raw                            ; .67         ; glo 390
Earth, Fullers, raw                            ; .673        ; sim
Ebonite                                        ; 1.15        ; aes 178
Fats                                           ; .9-.97      ; mar 6-7
Felted cattle hair                             ; .18-.21     ; hcp E5
Fertilizer, acid phosphate                     ; .96         ; glo 390
Fertilizer, acid phosphate                     ; .961        ; sim
Firebrick                                      ; 2.1         ; aes 177
Fish, meal                                     ; .59         ; glo 390
Fish, meal                                     ; .593        ; sim
Fish, scrap                                    ; .72         ; glo 390
Fish, scrap                                    ; .721        ; sim
Flax                                           ; 1.5         ; aes 182
Flax                                           ; 1.52        ; aes 172
Flaxseed, whole                                ; .72         ; glo 390
Flaxseed, whole                                ; .721        ; sim
Flour, loose                                   ; .4-.5       ; mar 6-7
Flour, pressed                                 ; .7-.8       ; mar 6-7
Flour, wheat                                   ; .59         ; glo 390
Flour, wheat                                   ; .593        ; sim
Flue dust                                      ; 1.45-2.02   ; sim
Foam, formaldehyde-urea (mipora)               ; .02         ; hep 45
Fullers Earth - raw or burnt                   ; .57-.73     ; sim
Garbage                                        ; .48         ; glo 390
Garbage, household rubbish                     ; .481        ; sim
Gelatin                                        ; 1.27        ; aes 178
Glass - broken or cullet                       ; 1.29-1.94   ; sim
Glass fiber                                    ; 2.5         ; aes 182
Glass wool (Pyrex, curled)                     ; .064-.16    ; hcp E5
Glass, common                                  ; 2.4-2.8     ; aes 178
Glass, common                                  ; 2.4-2.8     ; mar 6-7
Glass, crystal                                 ; 2.9-3       ; mar 6-7
Glass, flint                                   ; 2.9-5.9     ; aes 178
Glass, flint                                   ; 3.2-4.7     ; mar 6-7
Glass, plate or crown                          ; 2.45-2.72   ; mar 6-7
Glass, silica                                  ; 2.55        ; aes 182
Glass, window                                  ; 2.5         ; aes 177
Glass, window                                  ; 2.579       ; sim
Glass, window                                  ; 2.58        ; glo 390
Glue                                           ; 1.27        ; aes 178
Glue, animal, flaked                           ; .56         ; glo 390
Glue, animal, flaked                           ; .561        ; sim
Glue, vegetable, powdered                      ; .64         ; glo 390
Glue, vegetable, powdered                      ; .641        ; sim
Gluten, meal (protein from wheat)              ; .625        ; sim
Gluten, meal (protein from wheat)              ; .63         ; glo 390
Grain, barley                                  ; .6          ; sim
Grain, barley                                  ; 0.62        ; pht
Grain, corn, ear                               ; 0.9         ; pht
Grain, corn, shelled                           ; 0.72        ; pht
Grain, flax                                    ; 0.77        ; pht
Grain, maize                                   ; .76         ; sim
Grain, millet                                  ; .76-.8      ; sim
Grain, millet                                  ; 0.64        ; pht
Grain, oats                                    ; 0.41        ; pht
Grain, rice, hulled                            ; 0.75        ; pht
Grain, rice, rough                             ; 0.58        ; pht
Grain, rye                                     ; 0.72        ; pht
Grain, wheat                                   ; .78-.8      ; sim
Grain, wheat                                   ; 0.77        ; pht
Graphite (hexagonal sheet form of carbon)      ; 2.30-2.72   ; aes 178
Graphite whisker                               ; 1.7         ; aes 182
Graphite, brick                                ; 1.56        ; aes 180
Graphite, fine grain premium                   ; 1.73        ; aes 180
Graphite, flake                                ; .64         ; glo 390
Graphite, flake                                ; .641        ; sim
Graphite, plates                               ; 1.70        ; aes 180
Graphite, porous                               ; 1.04        ; aes 180
Gravel, dry 1/4 to 2 inch                      ; 1.682       ; sim
Gravel, dry, 1/4 to 2 inch                     ; 1.68        ; glo 390
Gravel, loose, dry                             ; 1.52        ; glo 390
Gravel, loose, dry                             ; 1.522       ; sim
Gravel, w/sand, natural                        ; 1.92        ; glo 390
Gravel, wet 1/4 to 2 inch                      ; 2.002       ; sim
Gravel, wet, 1/4 to 2 inch                     ; 2.00        ; glo 390
Gravel, with sand, natural                     ; 1.922       ; sim
Gum arabic                                     ; 1.3-1.4     ; aes 178
Gypsum board                                   ; .8          ; aes 177
Hair felt                                      ; .1          ; aes 177
Hairinsul (50% hair, 50% jute)                 ; .098        ; hcp E5
Hairinsul (75% hair, 25% jute)                 ; .1          ; hcp E5
Hay and straw, bales                           ; .32         ; mar 6-7
Hay, compressed                                ; .1          ; hep 45
Hay, fresh mown                                ; .05         ; hep 45
Hay, loose                                     ; .08         ; glo 390
Hay, pressed                                   ; .38         ; glo 390
Hemp                                           ; 1.48        ; aes 172
Hemp                                           ; 1.5         ; aes 182
Hops, moist                                    ; .56         ; glo 390
Ice                                            ; .917        ; aes 178
Ice, 0 deg C                                   ; .9          ; aes 177
Ice, crushed                                   ; .59         ; glo 390
Ice, crushed                                   ; .593        ; sim
Ice, solid                                     ; .919        ; sim
Ice, solid                                     ; .92         ; glo 390
Iron carbide (Fe3C)                            ; 7.69        ; aes 183
Iron oxide pigment                             ; .4          ; glo 390
Iron oxide pigment                             ; .4          ; sim
Iron sulphate - pickling tank - dry            ; 1.2         ; sim
Iron sulphate - pickling tank - wet            ; 1.29        ; sim
Iron whisker                                   ; 7.8         ; aes 182
Ivory                                          ; 1.83-1.92   ; aes 178
Ivory                                          ; 1.84        ; glo 390
Ivory                                          ; 1.842       ; sim
Jute (vegetable fiber)                         ; 1.5         ; aes 172
Kapok between burlap or paper                  ; .016-.032   ; hcp E5
Lanolin, refined                               ; .94         ; aes 159
Lard                                           ; .919        ; pht
Lead azide (explosive)                         ; 3.8         ; aes 399
Lead, red (Pb3O4 or 2 PbO*PbO2)                ; 3.684       ; sim
Lead, red (Pb3O4 or 2 PbO*PbO2)                ; 3.69        ; glo 390
Lead, white pigment ((PbCO3)2*Pb(OH)2)         ; 4.085       ; sim
Lead, white pigment ((PbCO3)2*Pb(OH)2)         ; 4.09        ; glo 390
Leather                                        ; .86-1.02    ; mar 6-7
Leather                                        ; .945        ; sim
Leather                                        ; .95         ; glo 390
Leather, dry                                   ; .86         ; aes 178
Leather, dry                                   ; .9          ; aes 177
Lignite, dry (fuel between coal and peat)      ; .801        ; sim
Lime, hydrated (Ca(OH)2)                       ; .48         ; glo 390
Lime, hydrated (Ca(OH)2)                       ; .481        ; sim
Lime, quick, fine (CaO)                        ; 1.20        ; glo 390
Lime, quick, fine (CaO)                        ; 1.201       ; sim
Lime, quick, lump (CaO)                        ; .849        ; sim
Lime, quick, lump (CaO)                        ; .85         ; glo 390
Lime, slaked (Ca(OH)2)                         ; 1.3-1.4     ; aes 178
Lime, stone, large                             ; 2.69        ; glo 390
Lime, stone, lump                              ; 1.54        ; glo 390
Lime, wet or mortar                            ; 1.54        ; sim
Linofelt (flax fibers between paper)           ; .074        ; hcp E5
Linoleum                                       ; 1.18        ; aes 178
Linseed, meal                                  ; .51         ; glo 390
Linseed, meal                                  ; .513        ; sim
Linseed, whole                                 ; .75         ; glo 390
Linseed, whole                                 ; .753        ; sim
Lithium 6 deuteride                            ; 0.82        ; pht
Lungs                                          ; 0.40        ; pht
Magnesium oxide                                ; 1.94        ; sim
Magnesium sulfate, crystal                     ; 1.12        ; glo 390
Magnesium sulphate, crystal                    ; 1.121       ; sim
Magnesium titanate                             ; 3.6         ; aes 262
Malt                                           ; .336        ; sim
Malt                                           ; .34         ; glo 390
Manganese oxide                                ; 1.92        ; glo 390
Manganese oxide                                ; 1.922       ; sim
Manure                                         ; .4          ; glo 390
Manure                                         ; .4          ; sim
Marl, wet, excavated                           ; 2.24        ; glo 390
Mayonnaise, light                              ; 1.0         ; pht
Mayonnaise, traditional                        ; 0.91        ; pht
Meerschaum (hydrated magnesium silicate)       ; .99-1.28    ; aes 178
Milk, powdered                                 ; .449        ; sim
Milk, powdered                                 ; .45         ; glo 390
Mineral wool blanket                           ; .1          ; aes 177
Mohair (hair of Angora goat)                   ; 1.32        ; aes 172
Molybdenum carbide (Mo2C)                      ; 9.0         ; aes 183
Molybdenum carbide (MoC)                       ; 8.2         ; aes 183
Monosodium glutamate                           ; 1.62        ; pht
Mortar, Portland cement                        ; 2.08-2.25   ; mar 6-7
Mortar, wet                                    ; 2.40        ; glo 390
Mortar, wet                                    ; 2.403       ; sim
Mud, fluid                                     ; 1.73        ; glo 390
Mud, fluid                                     ; 1.73        ; sim
Mud, packed                                    ; 1.906       ; sim
Mud, packed                                    ; 1.91        ; glo 390
Oats                                           ; .43         ; glo 390
Oats                                           ; .432        ; sim
Oats, bulk                                     ; .41         ; mar 6-7
Oats, rolled                                   ; .3          ; glo 390
Oats, rolled                                   ; .304        ; sim
Ochre (pigment)                                ; 3.5         ; aes 178
Oil cake (remains from pressing seeds for oil) ; .785        ; sim
Oyster shells                                  ; .8          ; sim
Oyster shells, ground                          ; .849        ; sim
Oyster shells, ground                          ; .85         ; glo 390
PETN (explosive)                               ; 1.6         ; aes 399
Paper                                          ; .7-1.15     ; aes 178
Paper                                          ; .7-1.15     ; mar 6-7
Paper                                          ; .9          ; aes 177
Paper, standard                                ; 1.2         ; glo 390
Paper, standard                                ; 1.201       ; sim
Paraffin                                       ; .72         ; glo 390
Paraffin                                       ; .87-.91     ; aes 178
Paraffin wax                                   ; .87-.91     ; mar 6-7
Paraffin wax                                   ; .9          ; aes 177
Peanuts, not shelled                           ; .27         ; glo 390
Peanuts, not shelled                           ; .272        ; sim
Peanuts, shelled                               ; .64         ; glo 390
Peanuts, shelled                               ; .641        ; sim
Peas                                           ; .7          ; hep 45
Peat blocks                                    ; .84         ; aes 178
Peat, dry                                      ; .4          ; sim
Peat, dry                                      ; .40         ; glo 390
Peat, moist                                    ; .8          ; glo 390
Peat, moist                                    ; .801        ; sim
Peat, wet                                      ; 1.12        ; glo 390
Peat, wet                                      ; 1.121       ; sim
Phenol (carbolic acid C6H5OH)                  ; 1.071       ; aes 90
Phosphorus                                     ; 2.339       ; sim
Phosphorus                                     ; 2.34        ; glo 390
Plaster                                        ; .849        ; sim
Plaster                                        ; .85         ; glo 390
Plaster, light                                 ; .7          ; aes 177
Plaster, sand                                  ; 1.8         ; aes 177
Porcelain                                      ; 2.3-2.5     ; aes 178
Porcelain                                      ; 2.4         ; glo 390
Porcelain                                      ; 2.403       ; sim
Porcelain                                      ; 2.5         ; aes 177
Potash (unspecified potassium salt)            ; 1.28        ; glo 390
Potassium chloride                             ; 2.0         ; glo 390
Potassium chloride                             ; 2.002       ; sim
Potatoes                                       ; .67         ; hep 45
Potatoes, piled                                ; .67         ; mar 6-7
Potatoes, white                                ; .769        ; sim
Potatoes, white                                ; .77         ; glo 390
Regranulated cork, 4-5 mm particles            ; .13         ; hcp E5
Regranulated cork, fine particles              ; .15         ; hcp E5
Resin                                          ; 1.07        ; aes 178
Resin, synthetic, crushed                      ; .56         ; glo 390
Resin, synthetic, crushed                      ; .561        ; sim
Rice grits                                     ; .689        ; sim
Rice grits                                     ; .69         ; glo 390
Rice, hulled                                   ; .75         ; glo 390
Rice, hulled                                   ; .753        ; sim
Rice, rough                                    ; .577        ; sim
Rice, rough                                    ; .58         ; glo 390
Rip-rap (broken rock used to line shorelines)  ; 1.6         ; sim
Rip-rap, limestone (rock along shorelines)     ; 1.3-1.4     ; mar 6-7
Rip-rap, sandstone (rock along shorelines)     ; 1.4         ; mar 6-7
Rip-rap, shale (broken rock lines shorelines)  ; 1.7         ; mar 6-7
Rock wool, loose                               ; .096        ; hcp E5
Rock wool, sheet form, felted                  ; .16         ; hcp E5
Rosin (pine resin)                             ; 1.07        ; glo 390
Rosin (pine resin)                             ; 1.073       ; sim
Rubber goods                                   ; 1-2         ; mar 6-7
Rubber, Buna N                                 ; 1.0         ; aes 156
Rubber, Buna S                                 ; 1.0         ; aes 156
Rubber, Butyl                                  ; .95         ; aes 156
Rubber, EPDM                                   ; .86         ; aes 156
Rubber, Hypalon                                ; 1.2         ; aes 156
Rubber, Neoprene                               ; 1.25        ; aes 156
Rubber, Polymethane                            ; 1.2         ; aes 156
Rubber, Silastic                               ; 1.0         ; aes 156
Rubber, Thiokol                                ; 1.4         ; aes 156
Rubber, Viton                                  ; 1.85        ; aes 156
Rubber, butadiene                              ; 1.0         ; aes 156
Rubber, caoutchouc (natural rubber)            ; .92-.96     ; mar 6-7
Rubber, caoutchouc (natural rubber)            ; .945        ; sim
Rubber, ground scrap                           ; .48         ; glo 390
Rubber, ground scrap                           ; .481        ; sim
Rubber, hard                                   ; 1.19        ; aes 178
Rubber, manufactured                           ; 1.52        ; glo 390
Rubber, manufactured                           ; 1.522       ; sim
Rubber, natural                                ; .93         ; aes 156
Rubber, soft, commercial                       ; 1.1         ; aes 178
Rubber, soft, pure gum                         ; .91-.93     ; aes 178
Rye                                            ; .705        ; sim
Rye                                            ; .71         ; glo 390
Salt (sodium chloride)                         ; 2.165       ; pht
Salt, coarse (NaCl)                            ; .80         ; glo 390
Salt, fine (NaCl)                              ; 1.2         ; glo 390
Salt, granulated, piled (NaCl)                 ; .77         ; mar 6-7
Saltpeter (KNO3)                               ; 1.2         ; glo 390
Saltpeter (KNO3)                               ; 1.201       ; sim
Saltpeter (KNO3)                               ; 2.11        ; mar 6-7
Sand and gravel, dry                           ; 1.73        ; glo 390
Sand and gravel, wet                           ; 2.0         ; glo 390
Sand with gravel, dry                          ; 1.65        ; sim
Sand with gravel, wet                          ; 2.02        ; sim
Sand, dry                                      ; 1.60        ; glo 390
Sand, dry                                      ; 1.602       ; sim
Sand, gravel, dry, loose                       ; 1.4-1.7     ; mar 6-7
Sand, gravel, dry, packed                      ; 1.6-1.9     ; mar 6-7
Sand, gravel, wet                              ; 1.89-2.16   ; mar 6-7
Sand, loose                                    ; 1.44        ; glo 390
Sand, loose                                    ; 1.442       ; sim
Sand, rammed                                   ; 1.68        ; glo 390
Sand, rammed                                   ; 1.682       ; sim
Sand, water filled                             ; 1.92        ; glo 390
Sand, water filled                             ; 1.922       ; sim
Sand, wet                                      ; 1.92        ; glo 390
Sand, wet                                      ; 1.922       ; sim
Sand, wet, packed                              ; 2.08        ; glo 390
Sand, wet, packed                              ; 2.082       ; sim
Sawdust                                        ; .15         ; aes 177
Sawdust                                        ; .21         ; sim
Sawdust                                        ; .27         ; glo 390
Sawdust, redwood                               ; .175        ; hcp E5
Sawdust, various woods                         ; .19         ; hcp E5
Serpentine (hydrated metamorphic rock)         ; 2.50-2.65   ; aes 178
Sewage, sludge                                 ; .721        ; sim
Sil-o-cel powdered diatomaceous earth          ; .17         ; hcp E5
Silicon                                        ; 2.33        ; pht
Silicon carbide (SiC)                          ; 3.22        ; aes 183
Silicon carbide whisker                        ; 3.2         ; aes 182
Silk                                           ; 1.25        ; aes 172
Sisal (fiber from agave plant)                 ; 1.49        ; aes 172
Skin                                           ; 1.05        ; pht
Slag (by-product of smelting ore)              ; 2.0-3.9     ; aes 178
Slag, broken                                   ; 1.76        ; glo 390
Slag, broken                                   ; 1.762       ; sim
Slag, crushed 1/4 inch                         ; 1.19        ; glo 390
Slag, crushed, 1/4 inch                        ; 1.185       ; sim
Slag, furnace granulated                       ; .96         ; glo 390
Slag, furnace granulated                       ; .961        ; sim
Slag, solid                                    ; 2.114       ; sim
Slag, solid                                    ; 2.12        ; glo 390
Snow, compacted                                ; .48         ; glo 390
Snow, compacted                                ; .481        ; sim
Snow, freshly fallen                           ; .16         ; glo 390
Snow, freshly fallen                           ; .16         ; sim
Soap powder                                    ; .37         ; glo 390
Soap, chips                                    ; .16         ; sim
Soap, chips or flakes                          ; .16         ; glo 390
Soap, flakes                                   ; .16         ; sim
Soap, powdered                                 ; .368        ; sim
Soap, solid                                    ; .8          ; glo 390
Soap, solid                                    ; .801        ; sim
Soda ash, heavy (Na2CO3, washing soda)         ; .96         ; glo 390
Soda ash, heavy (Na2CO3, washing soda)         ; 1.08        ; sim
Soda ash, light (Na2CO3, washing soda)         ; .43         ; glo 390
Soda ash, light (Na2CO3, washing soda)         ; .432        ; sim
Sodium aluminate, ground                       ; 1.153       ; sim
Sodium bicarbonate                             ; 2.2         ; pht
Sodium bicarbonate (baking soda) NaHCO3        ; 2.2         ; wp
Sodium carbonate (washing soda) Na2CO3         ; 2.25-2.54   ; wp
Sodium carbonate (washing soda) Na2CO3*10H2O   ; 1.44        ; hcp B165
Sodium nitrate, ground (NaNO3)                 ; 1.20        ; glo 390
Sodium nitrate, ground (NaNO3)                 ; 1.201       ; sim
Sodium thiosulfate (hypo) Na2S2O3              ; 1.667       ; web
Soy beans, whole                               ; .753        ; sim
Soybeans, whole                                ; .75         ; glo 390
Spermaceti (wax from sperm whale's head)       ; .95         ; aes 178
Starch                                         ; 1.53        ; aes 178
Starch                                         ; 1.53        ; mar 6-7
Starch, powdered                               ; .56         ; glo 390
Starch, powdered                               ; .561        ; sim
Sugar                                          ; 1.59        ; aes 178
Sugar, brown                                   ; .72         ; glo 390
Sugar, brown                                   ; .721        ; sim
Sugar, granulated                              ; .849        ; sim
Sugar, granulated                              ; .85         ; glo 390
Sugar, powdered                                ; .80         ; glo 390
Sugar, powdered                                ; .801        ; sim
Sugar, raw cane                                ; .96         ; glo 390
Sugar, raw cane                                ; .961        ; sim
Sugar, sucrose                                 ; 1.55        ; pht
Sugarbeet pulp, dry                            ; .208        ; sim
Sugarbeet pulp, dry                            ; .21         ; glo 390
Sugarbeet pulp, wet                            ; .21         ; glo 390
Sugarbeet pulp, wet                            ; .561        ; sim
Sugarcane                                      ; .27         ; glo 390
Sugarcane                                      ; .272        ; sim
Sulfur                                         ; 1.93-2.07   ; mar 6-7
Sulfur, lump                                   ; 1.31        ; glo 390
Sulfur, pulverized                             ; .96         ; glo 390
Sulfur, solid                                  ; 2.0         ; glo 390
TNT (explosive)                                ; 1.55        ; aes 399
Tallow (rendered beef or mutton fat)           ; .94         ; aes 178
Tanbark, ground (bark used in tanning hides)   ; .88         ; glo 390
Tanbark, ground (bark used in tanning hides)   ; .881        ; sim
Tantalum carbide (TaC)                         ; 14.1        ; aes 183
Tar                                            ; 1.153       ; sim
Thermofelt (felted jute and asbestos fibers)   ; .125-.16    ; hcp E5
Thermofill, powdered gypsum                    ; .42-.54     ; hcp E5
Titania TiO2 (rutile)                          ; 4.0         ; aes 262
Titanium carbide (TiC)                         ; 4.9         ; aes 183
Tobacco                                        ; .32         ; glo 390
Tobacco                                        ; .32         ; sim
Torpex (explosive)                             ; 1.7         ; aes 399
Tungsten carbide (W2C)                         ; 17.3        ; aes 183
Tungsten carbide (WC)                          ; 15.2        ; aes 183
Turf (lawn)                                    ; .4          ; sim
Turf (lawn)                                    ; .40         ; glo 390
Vanadium carbide (VC)                          ; 5.8         ; aes 183
Water, fresh-fallen snow                       ; .125        ; mar 6-7
Water, ice, -100 C                             ; 0.927       ; pht
Water, ice, -50 C                              ; 0.922       ; pht
Water, ice, 0 C                                ; 0.916       ; pht
Wax, bayberry (myrtle)                         ; .93         ; aes 159
Wax, carnauba (palm) from Brazil               ; 1.00        ; aes 159
Wax, sealing                                   ; 1.8         ; aes 178
Wax, yellow beeswax                            ; .96         ; aes 159
Wheat                                          ; .769        ; sim
Wheat                                          ; .77         ; glo 390
Wheat, bulk                                    ; .77         ; mar 6-7
Wheat, cracked                                 ; .67         ; glo 390
Wheat, cracked                                 ; .673        ; sim
Wood shavings, planer                          ; .14         ; hcp E5
Wool (fiber from sheep)                        ; 1.31        ; glo 390
Wool (fiber from sheep)                        ; 1.314       ; sim
Wool (fiber from sheep)                        ; 1.32        ; mar 6-7
Wool, cloth (fiber from sheep)                 ; .24         ; hep 45
Wool, felt (fiber from sheep)                  ; .3          ; aes 177
Wool, felt (fiber from sheep)                  ; .30         ; hep 45
Wool, fiber (from sheep)                       ; 1.32        ; aes 172
Wool, loose (fiber from sheep)                 ; .1          ; aes 177
Zinc oxide                                     ; .4          ; sim
Zinc oxide                                     ; .40         ; glo 390
Zirconium carbide (ZrC)                        ; 6.7         ; aes 183

category = plastic
ABS (acrylonitrile butadiene styrene)          ; 1.06-1.08   ; aes 137
Acetal (polyoxymethylene)                      ; 1.43        ; aes 137
Acrylic (Plexiglas, methylmethacrylate)        ; 1.18-1.20   ; aes 137
Alkyd resins                                   ; 1.24-2.6    ; aes 137
Bakelite (phenol formaldehyde resin)           ; 1.36        ; glo 390
Bakelite, solid (phenol formaldehyde resin)    ; 1.362       ; sim
Cellulose acetate                              ; 1.27-1.34   ; aes 137
Cellulose acetate butyrate                     ; 1.15-1.22   ; aes 137
Epoxy                                          ; 1.115       ; aes 137
Epoxy w/38% by vol carbon filaments            ; 1.42        ; aes 149
Epoxy w/65% by wt glass cloth                  ; 2.0         ; aes 149
Kapton polyimide                               ; 1.42        ; aes 152
Kel-F polychlorotrifluoroethylene polymer      ; 2.10        ; aes 152
Melamine formaldehyde, cellulose filled        ; 1.47-1.52   ; aes 137
Melamine formaldehyde, mineral filled          ; 1.78        ; aes 137
Mylar polyester                                ; 1.395       ; aes 152
Nylon (polyamide)                              ; 1.13-1.15   ; aes 137
Nylon (polyamide)                              ; 1.07        ; aes 182
Nylon 6/6 w/40% by wt 1/4" glass fibers        ; 1.41        ; aes 149
PVC, polyvinyl chloride                        ; 1.25        ; aes 152
PVC, polyvinyl chloride, plasticized           ; 1.15-1.35   ; aes 137
PVC, polyvinyl chloride, unmodified            ; 1.36-1.4    ; aes 137
Phenolic w/65% by wt glass cloth               ; 1.9         ; aes 149
Plastics, foamed                               ; .2          ; aes 177
Plastics, solid                                ; 1.2         ; aes 177
Polycarbonate                                  ; 1.2         ; aes 137
Polyester                                      ; 1.5-2.1     ; aes 137
Polyester w/45% wt chopped glass strands       ; 1.6         ; aes 149
Polyester w/65% by wt glass cloth              ; 1.8         ; aes 149
PET, polyester terephthalate                   ; 1.38        ; wp
Polyethylene                                   ; .93         ; aes 152
Polyethylene, high density                     ; .941-.965   ; aes 137
Polyethylene, low density                      ; .91-.925    ; aes 137
Polyethylene, medium density                   ; .926-.941   ; aes 137
Polypropylene                                  ; .90         ; aes 137
Polypropylene                                  ; .905        ; aes 152
Polystyrene                                    ; 1.04-1.08   ; aes 137
Polystyrene foam (Styrofoam)                   ; .04         ; wp
Polystyrene-acrylonitrile                      ; 1.05-1.1    ; aes 137
Polytetrafluoroethylene (Teflon)               ; 2.1-2.3     ; aes 137
Polytrifluorochloroethylene                    ; 2.1-2.3     ; aes 137
Silicones                                      ; 1.8-2.8     ; aes 137
Stryofoam                                      ; .04         ; wp
Teflon, FEP                                    ; 2.15        ; aes 152
Teflon, FEP w/glass cloth                      ; 2.2         ; aes 152
Teflon, TFE                                    ; 2.15        ; aes 152
Teflon, TFE w/glass cloth                      ; 2.2         ; aes 152
Urea formaldehyde                              ; 1.47-1.52   ; aes 137

category = wood
Afromosia (African teak)                       ; .705        ; sim
Alder                                          ; .42-.68     ; aes 178
Apple (wood)                                   ; .66-.84     ; aes 178
Apple (wood)                                   ; .71         ; glo 390
Apple (wood)                                   ; .66-.74     ; mar 6-7
Apple (wood)                                   ; .66-.83     ; sim
Ash (wood)                                     ; .65-.85     ; aes 178
Ash (wood)                                     ; .85         ; aes 178
Ash, black (wood)                              ; .54         ; glo 390
Ash, black (wood)                              ; .54         ; sim
Ash, black (wood)                              ; .55         ; mar 6-7
Ash, white (wood)                              ; .67         ; glo 390
Ash, white (wood)                              ; .64-.71     ; mar 6-7
Ash, white (wood)                              ; .67         ; sim
Aspen                                          ; .42         ; glo 390
Aspen                                          ; .42         ; sim
Balsa                                          ; .11-.14     ; aes 178
Balsa                                          ; .17         ; sim
Bamboo                                         ; .31-.40     ; aes 178
Bamboo                                         ; .3-.4       ; sim
Bark (wood)                                    ; .24         ; glo 390
Bark, wood refuse                              ; .24         ; sim
Basswood                                       ; .32-.59     ; aes 178
Beech (wood)                                   ; .70-.90     ; aes 178
Birch (wood)                                   ; .51-.77     ; aes 178
Birch (British)                                ; .67         ; sim
Birch plywood, 1/4" thick                      ; .345        ; mba
Birch, sweet, yellow                           ; .71-.72     ; mar 6-7
Birch, yellow                                  ; .71         ; glo 390
Blue gum (wood)                                ; 1.0         ; aes 178
Boxwood                                        ; .95-1.16    ; aes 178
Butternut (wood)                               ; .38         ; aes 178
Cedar (wood)                                   ; .49-.57     ; aes 178
Cedar, red                                     ; .38         ; sim
Cedar, red                                     ; .38         ; glo 390
Cedar, white, red                              ; .35         ; mar 6-7
Cherry (wood)                                  ; .56         ; glo 390
Cherry (wood)                                  ; .7-.9       ; aes 178
Cherry (wood)                                  ; .43         ; mar 6-7
Chestnut (wood)                                ; .48         ; glo 390
Chestnut (wood)                                ; .48         ; mar 6-7
Cottonwood                                     ; .42         ; glo 390
Cypress (wood)                                 ; .51         ; glo 390
Cypress (wood)                                 ; .45-.48     ; mar 6-7
Cypress (wood)                                 ; .51         ; sim
Dogwood                                        ; .76         ; aes 178
Douglas Fir                                    ; .53         ; sim
Ebony wood                                     ; .96         ; glo 390
Ebony wood                                     ; .96-1.12    ; sim
Ebony wood                                     ; 1.11-1.33   ; aes 178
Elm                                            ; .54-.60     ; aes 178
Elm                                            ; .56         ; glo 390
Elm (English)                                  ; .6          ; sim
Elm (Rock)                                     ; .815        ; sim
Elm (Wych)                                     ; .69         ; sim
Elm, white                                     ; .56         ; mar 6-7
Fiberboard, light                              ; .24         ; aes 177
Fiberboard, medium density (MDF)               ; .5-1        ; wp
Fir, Douglas                                   ; .53         ; glo 390
Fir, Douglas                                   ; .48-.55     ; mar 6-7
Fir, balsam                                    ; .4          ; mar 6-7
Hardboard, fiber                               ; 1.1         ; aes 177
Hardboard, high density (e.g. Masonite)        ; .8-1.04     ; wp
Hemlock (wood)                                 ; .4          ; glo 390
Hemlock (wood)                                 ; .45-.5      ; mar 6-7
Hickory (wood)                                 ; .60-.93     ; aes 178
Hickory (wood)                                 ; .85         ; glo 390
Hickory (wood)                                 ; .74-.8      ; mar 6-7
Holly (wood)                                   ; .76         ; aes 178
Iroko (African hardwood)                       ; .655        ; sim
Juniper (wood)                                 ; .56         ; aes 178
Larch (wood)                                   ; .50-.56     ; aes 178
Larch (wood)                                   ; .59         ; sim
Lignum Vitae (wood)                            ; 1.28-1.37   ; sim
Lignum vitae (wood)                            ; 1.17-1.33   ; aes 178
Lignum vitae (wood)                            ; 1.28        ; glo 390
Locust (wood)                                  ; .67-.71     ; aes 178
Locust (wood)                                  ; .71         ; glo 390
Locust (wood)                                  ; .67-.77     ; mar 6-7
Locust, dry (wood)                             ; .705        ; sim
Mahogany (wood)                                ; .56-.85     ; mar 6-7
Mahogany, African                              ; .495-.85    ; sim
Mahogany, Honduras                             ; .545        ; sim
Mahogany, Honduras                             ; .54         ; glo 390
Mahogany, Honduras                             ; .66         ; aes 178
Mahogany, Spanish                              ; .85         ; glo 390
Mahogany, Spanish                              ; .85         ; aes 178
Maple (wood)                                   ; .62-.75     ; aes 178
Maple (wood)                                   ; .71         ; glo 390
Maple (wood)                                   ; .755        ; sim
Maple, sugar (wood)                            ; .68         ; mar 6-7
Maple, white (wood)                            ; .53         ; mar 6-7
Oak (wood)                                     ; .60-.90     ; aes 178
Oak (wood)                                     ; .59-.93     ; sim
Oak, chestnut                                  ; .74         ; mar 6-7
Oak, live                                      ; .95         ; glo 390
Oak, live                                      ; .87         ; mar 6-7
Oak, red                                       ; .71         ; glo 390
Oak, red                                       ; .705        ; sim
Oak, red, black                                ; .64-.71     ; mar 6-7
Oak, white                                     ; .77         ; mar 6-7
Particle board, flat pressed                   ; .75         ; tow
Particle board, high density                   ; .75-1.3     ; tow
Particle board, low density                    ; .25-.45     ; tow
Particle board, medium density                 ; .55-.7      ; tow
Pear (wood)                                    ; .61-.73     ; aes 178
Pecan (wood)                                   ; .75         ; glo 390
Pecan (wood)                                   ; .753        ; sim
Pine, Canadian                                 ; .35-.56     ; sim
Pine, Oregon                                   ; .53         ; sim
Pine, Parana                                   ; .56         ; sim
Pine, Red                                      ; .37-.66     ; sim
Pine, Norway                                   ; .55         ; mar 6-7
Pine, Oregon                                   ; .51         ; mar 6-7
Pine, Southern                                 ; .61-.67     ; mar 6-7
Pine, pitch                                    ; .83-.85     ; aes 178
Pine, red                                      ; .48         ; mar 6-7
Pine, white                                    ; .35-.5      ; aes 178
Pine, white                                    ; .42         ; glo 390
Pine, white                                    ; .43         ; mar 6-7
Pine, yellow                                   ; .37-.60     ; aes 178
Pine, yellow, northern                         ; .54         ; glo 390
Pine, yellow, southern                         ; .72         ; glo 390
Plum (wood)                                    ; .66-.78     ; aes 178
Plywood, general                               ; .45-.53     ; web
Poplar (wood)                                  ; .35-.5      ; aes 178
Poplar (wood)                                  ; .43         ; mar 6-7
Pressed wood, pulp board                       ; .19         ; aes 178
Redwood (American)                             ; .45         ; sim
Redwood (European)                             ; .51         ; sim
Redwood, California                            ; .45         ; glo 390
Redwood, California                            ; .42         ; mar 6-7
Satinwood                                      ; .95         ; aes 178
Spruce (wood)                                  ; .48-.70     ; aes 178
Spruce, Canadian                               ; .45         ; sim
Spruce, Sitka                                  ; .45         ; sim
Spruce, California                             ; .45         ; glo 390
Spruce, white, red                             ; .45         ; mar 6-7
Sycamore (wood)                                ; .40-.60     ; aes 178
Sycamore (wood)                                ; .59         ; glo 390
Sycamore (wood)                                ; .59         ; sim
Teak (wood)                                    ; .63-.72     ; sim
Teak, African                                  ; .98         ; aes 178
Teak, African                                  ; .99         ; mar 6-7
Teak, Indian                                   ; .66-.88     ; aes 178
Teak, Indian                                   ; .66-.88     ; mar 6-7
Walnut (wood)                                  ; .64-.70     ; aes 178
Walnut, black (wood)                           ; .61         ; glo 390
Walnut, black (wood)                           ; .59         ; mar 6-7
Walnut, black, dry (wood)                      ; .609        ; sim
Water gum (wood)                               ; 1.0         ; aes 178
Willow (wood)                                  ; .4-.6       ; aes 178
Willow (wood)                                  ; .42         ; glo 390
Willow (wood)                                  ; .42         ; sim
Willow (wood)                                  ; .42-.5      ; mar 6-7
Wood chips, dry                                ; .24-.52     ; sim
Wood refuse                                    ; .24         ; glo 390

category = mineral
Agate                                          ; 2.5-2.7     ; aes 178
Alumina Al2O3                                  ; 3.68        ; aes 193
Alumina, 99.7% Al2O3                           ; 3.9         ; aes 262
Aluminum oxide                                 ; 1.52        ; glo 390
Aluminum oxide                                 ; 1.522       ; sim
Andesite, solid                                ; 2.771       ; sim
Asbestos                                       ; 2.1-2.8     ; mar 6-7
Barite, crushed (BaSO4)                        ; 2.883       ; sim
Barium titanate                                ; 5.5         ; aes 262
Baryte (BaSO4, barite)                         ; 4.5         ; mar 6-7
Basalt (igneous rock)                          ; 2.7-3.2     ; mar 6-7
Basalt, broken (igneous rock)                  ; 1.954       ; sim
Basalt, broken (igneous rock)                  ; 1.96        ; glo 390
Basalt, solid (igneous rock)                   ; 3.01        ; glo 390
Basalt, solid (igneous rock)                   ; 3.011       ; sim
Bauxite (aluminum ore)                         ; 2.55        ; mar 6-7
Bauxite, crushed (aluminum ore)                ; 1.28        ; glo 390
Bauxite, crushed (aluminum ore)                ; 1.281       ; sim
Bentonite (type of clay)                       ; .59         ; glo 390
Bentonite (type of clay)                       ; .593        ; sim
Beryllia BeO (beryllium oxide)                 ; 3.08        ; aes 262
Beryllium oxide BeO                            ; 3.04        ; aes 193
Borax (hydrated Na2B4O7)                       ; 1.7-1.8     ; mar 6-7
Borax, fine (hydrated Na2B4O7)                 ; .849        ; sim
Borax, fine (hydrated Na2B4O7)                 ; .85         ; glo 390
Calcium oxide CaO                              ; 3.20        ; aes 193
Calcspar (calcite CaCO3)                       ; 2.6-2.8     ; aes 178
Caliche (deposit of calcium carbonate)         ; 1.442       ; sim
Chalk (sedimentary rock, CaCO3)                ; 1.8-2.8     ; mar 6-7
Chalk (sedimentary rock, CaCO3)                ; 1.9-2.8     ; aes 178
Chalk (sedimentary rock, CaCO3)                ; 2.0         ; aes 177
Chalk, fine (sedimentary rock, CaCO3)          ; 1.12        ; glo 390
Chalk, fine (sedimentary rock, CaCO3)          ; 1.121       ; sim
Chalk, lumpy (sedimentary rock, CaCO3)         ; 1.44        ; glo 390
Chalk, lumpy (sedimentary rock, CaCO3)         ; 1.442       ; sim
Chalk, solid (sedimentary rock, CaCO3)         ; 2.499       ; sim
Chalk, solid (sedimentary rock, CaCO3)         ; 2.5         ; glo 390
Chromium ore                                   ; 2.162       ; sim
Cinnabar (mercury ore, HgS)                    ; 8.12        ; aes 178
Coal, anthracite                               ; 1.4-1.8     ; mar 6-7
Coal, anthracite, broken                       ; 1.105       ; sim
Coal, anthracite, solid                        ; 1.506       ; sim
Coal, bituminous                               ; 1.2-1.5     ; mar 6-7
Coal, bituminous, broken                       ; .833        ; sim
Coal, bituminous, solid                        ; 1.346       ; sim
Cobaltite (CoAsS + Fe, Ni)                     ; 6.295       ; sim
Copper ore                                     ; 1.94-2.59   ; sim
Corundum (crystalline Al2O3)                   ; 3.9-4.0     ; aes 178
Corundum, 90% Al2O3                            ; 3.20        ; aes 193
Cryolite (Na3AlF6)                             ; 1.6         ; glo 390
Cryolite (Na3AlF6)                             ; 1.602       ; sim
Cullet (scraps of broken glass)                ; 1.602       ; sim
Culm (waste from coal preparation)             ; .753        ; sim
Diamond (allotrope of carbon)                  ; 3.01-3.52   ; aes 178
Dolomite (CaMg(C)3)2)                          ; 2.84        ; aes 178
Dolomite (CaMg(C)3)2)                          ; 2.9         ; mar 6-7
Dolomite, lumpy (CaMg(C)3)2)                   ; 1.52        ; glo 390
Dolomite, lumpy (CaMg(C)3)2)                   ; 1.522       ; sim
Dolomite, pulverized (CaMg(C)3)2)              ; .737        ; sim
Dolomite, pulverized (CaMg(C)3)2)              ; .74         ; glo 390
Dolomite, solid (CaMg(C)3)2)                   ; 2.899       ; sim
Dolomite, solid (CaMg(C)3)2)                   ; 2.9         ; glo 390
Emery (usually mostly Al2O3)                   ; 4.0         ; aes 178
Emery (usually mostly Al2O3)                   ; 4.005       ; sim
Emery (usually mostly Al2O3)                   ; 4.01        ; glo 390
Feldspar (common crustal rock)                 ; 2.55-2.75   ; aes 178
Feldspar, pulverized (common crustal rock)     ; 1.23        ; glo 390
Feldspar, pulverized (common crustal rock)     ; 1.233       ; sim
Feldspar, solid (common crustal rock)          ; 2.56        ; glo 390
Feldspar, solid (common crustal rock)          ; 2.563       ; sim
Ferrofluids                                    ; .9-1.7      ; aes 312
Flint                                          ; 2.63        ; aes 178
Flint, silica                                  ; 1.39        ; sim
Fluorite (CaF2)                                ; 3.18        ; aes 178
Fluorspar, lumps (CaF2)                        ; 1.6         ; glo 390
Fluorspar, lumps (CaF2)                        ; 1.602       ; sim
Fluorspar, pulverized (CaF2)                   ; 1.44        ; glo 390
Fluorspar, pulverized (CaF2)                   ; 1.442       ; sim
Fluorspar, solid (CaF2)                        ; 3.204       ; sim
Fluorspar, solid (CaF2)                        ; 3.21        ; glo 390
Forsterite 2MgO*SiO2                           ; 2.56        ; aes 193
Galena (lead ore) PbS                          ; 7.3-7.6     ; aes 178
Galena (lead ore) PbS                          ; 7.4-7.6     ; sim
Garnet (variety of silicate minerals)          ; 3.15-4.3    ; aes 178
Gneiss, bed in place (metamorphic rock)        ; 2.867       ; sim
Gneiss, broken (metamorphic rock)              ; 1.858       ; sim
Granite (igneous rock)                         ; 2.6-2.7     ; mar 6-7
Granite (igneous rock)                         ; 2.64-2.76   ; aes 178
Granite, broken (igneous rock)                 ; 1.65        ; glo 390
Granite, broken (igneous rock)                 ; 1.65        ; sim
Granite, solid (igneous rock)                  ; 2.69        ; glo 390
Granite, solid (igneous rock)                  ; 2.691       ; sim
Graphite (carbon allotrope)                    ; 1.64-2.7    ; mar 6-7
Gummite (uranium ore)                          ; 3.89-6.4    ; sim
Gypsum CaSO4*2H20                              ; 2.30-2.37   ; hcp B222
Gypsum CaSO4*2H20                              ; 2.31-2.33   ; aes 178
Gypsum, broken                                 ; 1.29-1.6    ; sim
Gypsum, broken                                 ; 1.81        ; glo 390
Gypsum, crushed                                ; 1.60        ; glo 390
Gypsum, crushed                                ; 1.602       ; sim
Gypsum, pulverized                             ; 1.12        ; glo 390
Gypsum, pulverized                             ; 1.121       ; sim
Gypsum, solid                                  ; 2.787       ; sim
Gypsum, solid                                  ; 2.79        ; glo 390
Halite (NaCl salt), broken                     ; 1.506       ; sim
Halite (NaCl salt), solid                      ; 2.323       ; sim
Hematite (iron ore)                            ; 4.9-5.3     ; aes 178
Hematite (iron ore)                            ; 5.095-5.205 ; sim
Hematite (iron ore)                            ; 5.2         ; mar 6-7
Hematite (iron ore), broken                    ; 3.22        ; glo 390
Hematite (iron ore), solid                     ; 4.90        ; glo 390
Hemimorphite (zinc ore)                        ; 3.395-3.49  ; sim
Hornblende (complex series of minerals)        ; 3.0         ; aes 178
Ilmenite (FeTiO3)                              ; 2.307       ; sim
Iron ore, crushed                              ; 2.1-2.9     ; sim
Iron pyrite (FeS2)                             ; 2.4         ; sim
Kaolin, green crushed (Al2Si2O5(OH)4)          ; 1.025       ; sim
Kaolin, pulverized (Al2Si2O5(OH)4)             ; .352        ; sim
Lime, stone, large                             ; 2.691       ; sim
Lime, stone, lump                              ; 1.538       ; sim
Limestone (sedimentary rock CaCO3)             ; 2.1-2.86    ; mar 6-7
Limestone (sedimentary rock CaCO3)             ; 2.5         ; aes 177
Limestone (sedimentary rock CaCO3)             ; 2.68-2.76   ; aes 178
Limestone, broken (sedimentary rock CaCO3)     ; 1.55        ; glo 390
Limestone, broken (sedimentary rock CaCO3)     ; 1.554       ; sim
Limestone, pulverized (sedimentary rock CaCO3) ; 1.394       ; sim
Limestone, pulverized (sedimentary rock CaCO3) ; 1.55        ; glo 390
Limestone, solid (sedimentary rock CaCO3)      ; 2.61        ; glo 390
Limestone, solid (sedimentary rock CaCO3)      ; 2.611       ; sim
Limonite (iron ore)                            ; 2.467       ; mar 6-7
Limonite (iron ore), broken                    ; 2.467       ; sim
Limonite (iron ore), solid                     ; 3.796       ; sim
Magnesia (85%)                                 ; .25         ; aes 177
Magnesia MgO                                   ; 3.36        ; aes 193
Magnesite (MgCO3)                              ; 3.0         ; mar 6-7
Magnesite, solid (MgCO3)                       ; 3.011       ; sim
Magnesium oxide MgO                            ; 2.80        ; aes 193
Magnetite (Fe3O4), broken                      ; 3.284       ; sim
Magnetite (Fe3O4), solid                       ; 5.046       ; sim
Magnetite Fe3O4                                ; 4.9-5.2     ; aes 178
Malachite (copper ore)                         ; 3.7-4.1     ; aes 178
Malachite (copper ore)                         ; 3.75-3.96   ; sim
Marble (metamorphic rock)                      ; 2.6         ; aes 177
Marble (metamorphic rock)                      ; 2.6-2.84    ; aes 178
Marble (metamorphic rock)                      ; 2.6-2.86    ; mar 6-7
Marble, broken (metamorphic rock)              ; 1.57        ; glo 390
Marble, broken (metamorphic rock)              ; 1.57        ; sim
Marble, solid (metamorphic rock)               ; 2.56        ; glo 390
Marble, solid (metamorphic rock)               ; 2.563       ; sim
Marl, wet, excavated                           ; 2.243       ; sim
Mica                                           ; 2.6-3.2     ; aes 178
Mica                                           ; 2.7         ; aes 177
Mica, broken                                   ; 1.60        ; glo 390
Mica, broken                                   ; 1.602       ; sim
Mica, flake                                    ; .52         ; sim
Mica, powder                                   ; .986        ; sim
Mica, solid                                    ; 2.88        ; glo 390
Mica, solid                                    ; 2.883       ; sim
Molybdenum ore                                 ; 1.6         ; sim
Mullite 3Al2O3*SiO2                            ; 2.56        ; aes 193
Muscovite (common mica, isinglass)             ; 2.76-3.00   ; aes 178
Nickel ore                                     ; 1.6         ; sim
Opal                                           ; 2.2         ; aes 178
Phosphate rock, broken                         ; 1.762       ; sim
Platinum ore                                   ; 2.6         ; sim
Porphyry (low-grade copper ore)                ; 2.6-2.9     ; mar 6-7
Porphyry, broken (low-grade copper ore)        ; 1.65        ; sim
Porphyry, solid (low-grade copper ore)         ; 2.547       ; sim
Potash (various potassium salts)               ; 1.281       ; sim
Pumice stone (volcanic rock)                   ; .64         ; glo 390
Pumice stone (volcanic rock)                   ; .641        ; sim
Pumice, natural (volcanic rock)                ; .37-.9      ; mar 6-7
Pyrite (fool's gold, FeS2)                     ; 2.4-5.015   ; sim
Pyrite (fool's gold, FeS2)                     ; 4.95-5.1    ; aes 178
Quartz (SiO2)                                  ; 2.65        ; aes 178
Quartz sand (SiO2)                             ; 1.201       ; sim
Quartz whisker (SiO2)                          ; 2.65        ; aes 182
Quartz, clear fused (SiO2)                     ; 2.2         ; aes 187
Quartz, flint                                  ; 2.5-2.8     ; mar 6-7
Quartz, lump (SiO2)                            ; 1.55        ; glo 390
Quartz, lump (SiO2)                            ; 1.554       ; sim
Quartz, sand (SiO2)                            ; 1.20        ; glo 390
Quartz, solid (SiO2)                           ; 2.64        ; glo 390
Quartz, solid (SiO2)                           ; 2.643       ; sim
Rock salt (NaCl, halide)                       ; 2.18        ; aes 178
Rock, soft, dug with shovel                    ; 1.6-1.78    ; sim
Salt cake (Na2SO4)                             ; 1.442       ; sim
Salt, coarse (NaCl, halide)                    ; .801        ; sim
Salt, fine (NaCl, halide)                      ; 1.201       ; sim
Sandstone (sedimentary rock)                   ; 2-2.5       ; mar 6-7
Sandstone (sedimentary rock)                   ; 2.14-2.36   ; aes 178
Sandstone (sedimentary rock)                   ; 2.3         ; aes 177
Sandstone, broken (sedimentary rock)           ; 1.37-1.45   ; sim
Sandstone, broken (sedimentary rock)           ; 1.51        ; glo 390
Sandstone, solid (sedimentary rock)            ; 2.32        ; glo 390
Sandstone, solid (sedimentary rock)            ; 2.323       ; sim
Sapphire or Al203 whisker                      ; 4.0         ; aes 182
Shale, broken (sedimentary rock)               ; 1.586       ; sim
Shale, broken (sedimentary rock)               ; 1.59        ; glo 390
Shale, slate (sedimentary rock)                ; 2.6-2.9     ; mar 6-7
Shale, solid (sedimentary rock)                ; 2.675       ; sim
Shale, solid (sedimentary rock)                ; 2.68        ; glo 390
Silica SiO2                                    ; 1.76        ; aes 193
Silica, fused translucent (SiO2)               ; 2.07        ; aes 178
Silica, fused transparent (SiO2)               ; 2.21        ; aes 178
Silicon carbide SiC                            ; 2.72        ; aes 193
Silicon dioxide (quartz)                       ; 2.6         ; pht
Slate (metamorphic rock)                       ; 2.6-3.3     ; aes 178
Slate, broken (metamorphic rock)               ; 1.29-1.45   ; sim
Slate, broken (metamorphic rock)               ; 1.67        ; glo 390
Slate, pulverized (metamorphic rock)           ; 1.36        ; glo 390
Slate, pulverized (metamorphic rock)           ; 1.362       ; sim
Slate, solid (metamorphic rock)                ; 2.69        ; glo 390
Slate, solid (metamorphic rock)                ; 2.691       ; sim
Smithsonite (zinc ore)                         ; 4.3         ; sim
Soapstone (steatite, metamorphic rock)         ; 2.6-2.8     ; aes 178
Soapstone, talc (steatite, metamorphic rock)   ; 2.4         ; sim
Soapstone, talc (steatite, metamorphic rock)   ; 2.6-2.8     ; mar 6-7
Spinel MgAl2O4                                 ; 3.6-4.1     ; wp
Spinel MgO*Al2O3                               ; 3.52        ; aes 193
Stone (common, generic)                        ; 2.515       ; sim
Stone, crushed                                 ; 1.6         ; glo 390
Stone, crushed                                 ; 1.602       ; sim
Sulfur, lump                                   ; 1.314       ; sim
Sulfur, pulverized                             ; .961        ; sim
Sulfur, solid                                  ; 2.002       ; sim
Taconite (iron-bearing sedimentary rock)       ; 2.803       ; sim
Talc (magnesium silicate)                      ; 2.7-2.8     ; aes 178
Talc, broken (magnesium silicate)              ; 1.746       ; sim
Talc, broken (magnesium silicate)              ; 1.75        ; glo 390
Talc, solid (magnesium silicate)               ; 2.69        ; glo 390
Talc, solid (magnesium silicate)               ; 2.691       ; sim
Tar, bituminous                                ; 1.2         ; mar 6-7
Titanium oxide TiO2                            ; 4.17        ; aes 193
Topaz (silicate mineral)                       ; 3.5-3.6     ; aes 178
Tourmaline (boron silicate mineral)            ; 3.0-3.2     ; aes 178
Trap rock (e.g. basalt), broken                ; 1.746       ; sim
Trap rock (e.g. basalt), solid                 ; 2.883       ; sim
Vermiculite (hydrated phyllosilicate)          ; .13         ; aes 177
Zircon ZrO2*SiO2                               ; 3.52        ; aes 193
Zirconium oxide ZrO2                           ; 5.77        ; aes 193

category = gas
Acetylene C2H2 (20 C & 1 atm)                  ; 0.001084    ; aes 38
Air (20 C & 1 atm)                             ; 0.001204    ; aes 38
Air, 100 K                                     ; 0.003556    ; pht
Air, 1000 K                                    ; 0.000340    ; pht
Air, 200 K                                     ; 0.001746    ; pht
Air, 293 K                                     ; 0.001207    ; pht
Air, 300 K                                     ; 0.001161    ; pht
Air, 500 K                                     ; 0.000696    ; pht
Ammonia, anhydrous NH3 (20 C & 1 atm)          ; 0.0007104   ; aes 38
Argon (20 C & 1 atm)                           ; 0.0007104   ; aes 38
Argon, gas, ~300 K                             ; 0.001449    ; pht
Argon, liquid, 87 K                            ; 0.00143     ; pht
Butane (20 C & 1 atm)                          ; 0.002492    ; aes 38
Carbon dioxide (20 C & 1 atm)                  ; 0.00183     ; aes 38
Carbon dioxide, gas, +25 C                     ; 1.799       ; pht
Carbon dioxide, solid, -78 C                   ; 1.562       ; pht
Carbon monoxide (20 C & 1 atm)                 ; 0.001164    ; aes 38
Carbon, diamond                                ; 3.539       ; pht
Chlorine (20 C & 1 atm)                        ; 0.00295     ; aes 38
Ethane (20 C & 1 atm)                          ; 0.001252    ; aes 38
Fluorine (20 C & 1 atm)                        ; 0.001577    ; aes 38
Fluorocarbon CCl3F, Refrig. 11 (20 C & 1 atm)  ; 0.005707    ; aes 38
Freon 12, vapor                                ; 0.003683    ; pht
Helium (20 C & 1 atm)                          ; 0.0001662   ; aes 38
Helium, gas, ~300 K                            ; 0.000164    ; pht
Hydrogen (20 C & 1 atm)                        ; 0.00008429  ; aes 38
Hydrogen (H2), gas, 300 K                      ; 0.000082    ; pht
Hydrogen chloride (20 C & 1 atm)               ; 0.001517    ; aes 38
Hydrogen sulfide (20 C & 1 atm)                ; 0.001421    ; aes 38
Krypton (20 C & 1 atm)                         ; 0.00348     ; aes 38
Laughing gas N20 (20 C & 1 atm)                ; 0.00183     ; aes 38
Methane (20 C & 1 atm)                         ; 0.0006671   ; aes 38
Methyl chloride (20 C & 1 atm)                 ; 0.002095    ; aes 38
Natural gas (16% methane) (20 C & 1 atm)       ; 0.000722    ; aes 389
Neon (20 C & 1 atm)                            ; 0.0008393   ; aes 38
Nitric oxide NO (20 C & 1 atm)                 ; 0.001252    ; aes 38
Nitrogen (20 C & 1 atm)                        ; 0.001164    ; aes 38
Nitrogen (N2), gas, ~300 K                     ; 0.001145    ; pht
Oxygen (20 C & 1 atm)                          ; 0.001331    ; aes 38
Oxygen, gas, ~300 K                            ; 0.001308    ; pht
Ozone (20 C & 1 atm)                           ; 0.001999    ; aes 38
Propane (20 C & 1 atm)                         ; 0.00183     ; aes 38
Steam (H2O) saturated (0 C & 0.00603 atm)      ; 0.000004847 ; aes 18
Steam (H2O) saturated (100 C & 1 atm)          ; 0.0005977   ; aes 18
Steam (H2O) saturated (150 C & 4.70 atm)       ; 0.002548    ; aes 18
Steam (H2O) saturated (20 C & 0.023 atm)       ; 0.00001729  ; aes 18
Steam (H2O) saturated (200 C & 15.34 atm)      ; 0.007864    ; aes 18
Steam (H2O) saturated (250 C & 39.25 atm)      ; 0.02000     ; aes 18
Steam (H2O) saturated (300 C & 84.80 atm)      ; 0.04619     ; aes 18
Steam (H2O) saturated (350 C & 163.19 atm)     ; 0.1136      ; aes 18
Steam (H2O) saturated (50 C & 0.123 atm)       ; 0.00008302  ; aes 18
Sulfur dioxide (20 C & 1 atm)                  ; 0.002661    ; aes 38
Xenon (20 C & 1 atm)                           ; 0.005455    ; aes 38
'''

references = {
    "aes" : (
'''Bolz & Tuve, "Handbook of Tables for Applied Engineering''',
'''Science", 2nd ed., CRC Press, 1973.'''),
    "asm" : (
'''American Society of Metals, "Metals Handbook", Vol. 1,''',
'''8th ed., 1961 (9th printing, Aug 1977).'''), 
    "ceh" : (
'''Perry (ed.), "Chemical Engineers' Handbook", 5th ed.,''',
'''McGraw-Hill, 1973.'''),
    "el"  : ('''Emsley, "The Elements", Oxford, 1989.''',),
    "glo" : ('''Glover, "Pocket Ref", Sequoia Publishing, 1993.''',),
    "hcp" : (
'''Weast (ed.), "CRC Handbook of Chemistry and Physics",''',
'''CRC, 59th ed., 1978.'''),
    "hep" : (
'''Koshkin & Shirkevich, "Handbook of Elementary Physics",''',
'''3rd ed., MIR Publishers, 1977.'''),
    "mar" : (
'''Marks, "Standard Handbook for Mechanical Engineers",''',
'''7th ed., McGraw-Hill, 1967.  Note you can get an''',
'''electronic form of the 1916 edition of this book from''',
'''Google books (it's a big download, but it's an''',
'''excellent reference).'''),
    "mba" : ("Measured by script author.",),
    "mh"  : (
'''Oberg, Jones, Horton, "Machinery's Handbook", 21st''',
'''ed., Industrial Press, 1979.'''),
    "pht" : ('''Physics Hypertextbook''',
'''http://physics.info/density/'''),
    "sim" : (
"http://www.simetric.co.uk/si_materials.htm; accessed",
"27 Jan 2013."),
    "tow" : (
"http://www.towood.com/news_detail.php?id=412; accessed",
"27 Jan 2013.  Only used for particle board."),
    "web" : ("From web, location and date not noted.",),
    "wp"  : (
"Wikipedia http://en.wikipedia.org, accessed various",
"pages on various dates.",
    ),
}

categories = (
    "all",
    "gas",
    "liquid",
    "metal",
    "mineral",
    "misc",
    "plastic",
    "wood",
)

# The following are allowed units.  The numbers are what a density in
# g/cc should be multiplied by to get the density in the desired unit.
# Note pounds (lb) are pounds mass.  Unit conversion factors were
# (mostly) gotten from the GNU units program.
allowed_units = {
    "g/cc"      : 1,
    "mg/dl"     : 1e5,
    "mg/dL"     : 1e5,
    "g/mL"      : 1,
    "g/ml"      : 1,
    "kg/5gal"   : 18.9271,
    "kg/L"      : 1,
    "kg/l"      : 1,
    "kg/m3"     : 1000,
#   "kg/m^3"    : 1000,
    "lb/5gal"   : 41.727,
    "lb/ft3"    : 62.43,
#   "lb/ft^3"   : 62.43,
    "lb/gal"    : 8.345,
    "lb/in3"    : 0.03613,
#   "lb/in^3"   : 0.03613,

    # The following units are specific to the author, as they capture
    # the volumes of various things around his home he uses for moving
    # things.  If you want to use similar units, change things
    # appropriately.
    "kg/HFcart"    : 333,
    "lb/HFcart"    : 734,
    # HF cart dimensions:  16" high x 41" long x 31" wide
}

def Usage(d, status=1):
    name = sys.argv[0]
    s = '''
Usage:  {name} [options] [cmd [unit]]
  Look up material densities or find materials within a specified
  density range.  cmd can be a number or a string.  

  Typical uses:
    * Identify a material from its measured density (this is
      approximate, as densities given in the literature can vary
      substantially).
    * Find the density of a substance.
    * Find substances that are close in density to a given density.
    * Work with density units that are convenient to you (it's easy 
      to add new units if your favorite isn't present).

  If cmd is a number, it is interpreted as a density and the script
  will print out materials that are within 5% of the indicated density
  (use the -t option to change this tolerance).  The number will be
  interpreted in the indicated unit if it is given; if unit is not
  present, g/cc is assumed.  Since some densities are stored
  internally as a range, the tolerance is ignored for such densities
  and only printed if cmd lies within the indicated range.

  If cmd is a string, then it is a python regular expression that is
  used to search for densities of materials whose names match this
  expression.  The search is case-insensitive.  If unit is given when
  cmd is a string, it is interpreted as the input unit.

  All densities in the script are at about 20 degrees C and 1 atm
  pressure unless otherwise stated in the description.

  You can limit the output information by restricting the search to a
  particular category with the -c option.  For example, you might want
  to search only for metals with an indicated density.  Use the -C
  option to see the allowed category numbers (you can also use a few
  letters of the category name).

  When a solution is given in %, this is a mass percent.  The mass of
  the solute is that percentage of the total mass of solution.  For
  example, a 15% sodium chloride solution has 15 g of NaCl for every
  100 g of solution.

Examples:
    python density.py .
        Show densities of all materials in g/cc, sorted by density.  Use 
        -n to sort by name.

    python -u lb/ft3 -t 3 2500 kg/m3
        Show materials that are within 3% of a density of 2500 kg/m3.
        Show the displayed densities in pounds per cubic foot.
        steel.

Options:
    -C
        Print out the allowed category numbers and names.
    -c category
        Limit the search to the indicated category number.
    -d digits
        Define the number of significant figures to print the output
        report.  Defaults to 3.
    -n
        Sort output by the material's name (by default, the output is
        sorted by density).
    -R
        Print the list of references
    -r density
        Print results relative to the given density in g/cc.
    -t tol
        Change the search tolerance for when cmd is a number.  The
        materials printed are those that lie within cmd +/- tol where
        tol is in percent.  If the cmd value is within a range, the
        range is printed.  Default is 5%.
    -u unit
        Set the output unit for the density (defaults to g/cc).  Use
        the -U option to see the allowed unit strings.
    -U
        Print the allowed density units for the -u option.
'''[1:-1]
    out(s.format(**locals()))
    sys.exit(status)

def ParseCommandLine(d):
    d["-c"] = 0         # Category to print
    d["-d"] = 3         # Number of significant digits
    d["-n"] = False     # Sort by name
    d["-r"] = 1         # Relative to indicated density in g/cc
    d["-u"] = "g/cc"    # Output units
    d["-t"] = 5         # Tolerance in percent
    if len(sys.argv) < 2:
        Usage(d)
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "Cc:d:nRr:t:u:U")
    except getopt.GetoptError as e:
        msg, option = e
        out(msg)
        exit(1)
    for opt in optlist:
        if opt[0] == "-C":
            out("Categories (0 is default):")
            for i, cat in enumerate(categories):
                out(" ", i, cat)
            exit(0)
        elif opt[0] == "-c":
            try:
                d["-c"] = int(opt[1])
                n = len(categories)
                if not (0 <= d["-c"] <= n):
                    Error("-c option must be integer from 0 to %d" % n)
            except ValueError:
                # See if it's an acceptable string
                n = GetCategory(opt[1])
                if n is not None:
                    d["-c"] = n
                else:
                    Error("'%s' is not adequate to identify the category" %
                          opt[1])
        elif opt[0] == "-d":
            try:
                d["-d"] = int(opt[1])
            except ValueError:
                Error("-d option of '%s' is not an integer" % opt[1])
            if not (1 <= d["-d"] <= 15):
                Error("-d option must be integer from 1 to 15")
        elif opt[0] == "-R":
            out("Density references:\n")
            keys = references.keys()
            keys.sort()
            for k in keys:
                if k == "sim" and ignore_ref_sim:
                    continue
                out(k)
                for i in references[k]:
                    out("   ", i)
            exit(0)
        elif opt[0] == "-r":  # Print relative to given density in g/cc
            try:
                d["-r"] = float(opt[1])
            except ValueError:
                Error("-r option of '%s' is not a number" % opt[1])
            if d["-r"] <= 0:
                Error("-r option must be > 0")
        elif opt[0] == "-n":  # Sort by name
            d["-n"] = True
        elif opt[0] == "-t":  # Set density tolerance in %
            try:
                d["-t"] = float(opt[1])
            except ValueError:
                Error("-t option of '%s' is not a number" % opt[1])
            if d["-t"] <= 0:
                Error("-t option must be a percentage > 0")
        elif opt[0] == "-u":  # Set output unit
            d["-u"] = opt[1]
            if d["-u"] not in allowed_units:
                Error("'%s' is an unrecognized unit" % d["-u"])
        elif opt[0] == "-U":  # Show allowed unit strings
            out("Allowed unit strings are:")
            units = allowed_units.keys()
            units.sort()
            for i in units:
                out(" ", i)
            exit(0)
    if len(args) == 1:
        args.append(None)
    if len(args) != 2:
        Usage(d)
    return args

def GetCategory(s):
    '''See if we can identify the category number from the string s;
    partial matches OK.
    '''
    found, s = [], s.lower()
    for i, cat in enumerate(categories):
        if cat.find(s) == 0:
            found.append(i)
    if len(found) == 1:
        return found[0]
    else:
        return None

def out(*v, **kw):
    sep = kw.setdefault("sep", " ")
    nl  = kw.setdefault("nl", True)
    stream = kw.setdefault("stream", sys.stdout)
    if v:
        stream.write(sep.join([str(i) for i in v]))
    if nl:
        stream.write("\n")

def Error(msg, status=1):
    out(msg, stream=sys.stderr)
    exit(status)

def GetData(d):
    '''Return a tuple of the material data; each entry will be
       (name, spgr, ref, cat)
    where name is a string, spgr is the density in g/cc, ref is an
    integer which indicates which reference the number came from, and
    cat is the category number.  Note that spgr is a string that
    either represents a float or two floats separated by a hyphen.
    '''
    lines = data.split("\n")
    densities = set()
    for line in lines:
        line = line.strip()
        if not line or line[0] == "#":
            continue
        loc = line.find("category")
        if loc == 0:
            c = line.split("=")[1].strip()
            cat = categories.index(c)
            continue
        name, spgr, ref = line.split(";")
        name = name.strip()
        spgr = spgr.strip()
        ref = ref.strip()
        if ignore_ref_sim and ref == "sim":
            continue
        if not d["-c"] or (d["-c"] and cat == d["-c"]):
            densities.add((name, spgr, ref, cat))
    densities = list(densities)
    densities.sort()
    if 0:
        for name, spgr, ref, cat in densities:
            out("%-45s %-15s %-12s %d" % (name, spgr, ref, cat))
        exit()
    return tuple(densities)

def InterpDensity(s):
    '''Return a tuple of (low, high) or (nominal, None) that
    represents the density given in the string s.
    '''
    if "-" in s:
        return tuple([float(i) for i in s.split("-")])
    else:
        return (float(s), None)

def Report(results, d):
    if not results:
        out("No matches")
        return
    maxname, maxs, maxref = 0, 0, 0
    for name, s, ref in results:
        maxname = max(maxname, len(name))
        maxs = max(maxs, len(s))
        maxref = max(maxref, len(ref))
    out("Matching densities (units are %s):" % d["-u"])
    if d["-r"] != 1:
        out("   ** Densities are relative to %s g/cc **" % sig(d["-r"]))
    out()
    sname = "-"*maxname
    ss = "-"*maxs
    sref = "-"*maxref
    maxname += 3
    maxs += 3
    maxref += 3
    tname, ts, tref = "Material", "Density", "Ref"
    indent = ""
    t = "{indent}{tname:^{maxname}} {ts:^{maxs}} {tref:^{maxref}}"
    out(t.format(**locals()))
    t = "{indent}{sname:{maxname}} {ss:^{maxs}} {sref:^{maxref}}"
    out(t.format(**locals()))
    for name, s, ref in results:
        t = "{indent}{name:{maxname}} {s:^{maxs}} {ref:^{maxref}}"
        out(t.format(**locals()))

def FindDensity(density, unit, d):
    '''density is the density in the user wants to search for.
    unit is the string that specifies the units the density are in;
    note we must convert density to g/cc.  d is the options dictionary.
    '''
    tolerance = d["-t"]/100 + 1
    relative_to = d["-r"]
    sort_by_name = d["-n"]
    results = []
    if unit is None:
        unit = "g/cc"
    density *= 1/allowed_units[unit]     # Convert density in "unit" to g/cc
    conv_factor = allowed_units[d["-u"]] # Converts to output density
    for name, spgr, ref, cat in d["materials"]:
        # If the density of this material is in range, put the data
        # into the results array.
        low, high = InterpDensity(spgr)
        r = [name, low, high, ref]
        if high is None:
            if density/tolerance <= low <= density*tolerance:
                results.append(r)
        else:
            if (low <= density <= high):
                results.append(r)
    # Sort the results
    if sort_by_name:
        results.sort()
    else:
        # Sort by the second item = low
        k = 1
        f = lambda x, y: -1 if x[k] < y[k] else 0 if x[k] == y[k] else 1
        results.sort(f)
    # Change low and high to their formatted values
    for i, item in enumerate(results):
        name, low, high, ref = item
        low *= conv_factor/relative_to
        if high is None:
            s = sig(low)
        else:
            high *= conv_factor/relative_to
            s = sig(low) + "-" + sig(high)
        results[i] = (name, s, ref)
    Report(results, d)

def PerformTextSearch(cmd, unit, d):
    '''cmd is a text string representing a python regular expression.
    Find all materials whose description match this regular
    expression.  unit is the string to convert the output display to.
    d is the options dictionary.  If cmd can't be compiled as a
    regular expression, then it will just be used for a
    case-insensitive string search.
    '''
    relative_to = d["-r"]
    sort_by_name = d["-n"]
    if unit is not None:
        d["-u"] = unit
        conv_factor = allowed_units[unit]
    else:
        conv_factor = allowed_units[d["-u"]]
    no_regexp = False
    try:
        r = re.compile(cmd, re.I)
    except re.error:
        no_regexp = True
    results = []
    # Find names that match
    for name, spgr, ref, cat in d["materials"]:
        low, high = InterpDensity(spgr)
        t = [name, low, high, ref]
        if no_regexp:
            if name.lower().find(cmd.strip()) != -1:
                results.append(t)
        else:
            mo = r.search(name)
            if mo:
                results.append(t)
    # Sort the results
    if sort_by_name:
        results.sort()
    else:
        # Sort by the second item = low
        k = 1
        f = lambda x, y: -1 if x[k] < y[k] else 0 if x[k] == y[k] else 1
        results.sort(f)
    # Change low and high to their formatted values
    for i, item in enumerate(results):
        name, low, high, ref = item
        low *= conv_factor/relative_to
        if high is None:
            s = sig(low)
        else:
            high *= conv_factor/relative_to
            s = sig(low) + "-" + sig(high)
        results[i] = (name, s, ref)
    Report(results, d)

if __name__ == "__main__":
    d = {} # Options dictionary
    cmd, unit = ParseCommandLine(d)
    d["materials"] = GetData(d)
    sig.digits = d["-d"]
    try:
        density = float(cmd)
    except ValueError:
        PerformTextSearch(cmd, unit, d)
    else:
        FindDensity(density, unit, d)
