from enum import Enum

class BatchApplication(Enum):
    DEDUP = ("0,1,2,3",
         "dedup",
         "anakli/cca:parsec_dedup",
         "./run -a run -S parsec -p dedup -i native -n 1")
    
    BLACKSHOLES = ("0,1,2,3",
                "blackscholes",
                "anakli/cca:parsec_blackscholes",
                "./run -a run -S parsec -p blackscholes -i native -n 2")
    
    CANNEAL = ("0,1,2,3",
           "canneal",
           "anakli/cca:parsec_canneal",
           "./run -a run -S parsec -p canneal -i native -n 2")
    
    FREQMINE = ("0,1,2,3",
            "freqmine",
            "anakli/cca:parsec_freqmine",
            "./run -a run -S parsec -p freqmine -i native -n 2")
    
    FERRET = ("0,1,2,3",
          "ferret",
          "anakli/cca:parsec_ferret",
          "./run -a run -S parsec -p ferret -i native -n 3")
    
    VIPS = ("0,1,2,3",
        "vips",
        "anakli/cca:parsec_vips",
        "./run -a run -S parsec -p vips -i native -n 2")
    
    RADIX = ("0,1,2,3",
            "radix",
            "anakli/cca:parsec_radix",
            "./run -a run -S parsec -p radix -i native -n 2")