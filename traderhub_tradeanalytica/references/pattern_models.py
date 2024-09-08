PATTERN_MODEL = [
    {
        "name": "Head And Shoulders",
        "parametres": [
            {
                "name": "Window",
                "type": "int",
                "default": 5
            },
            {
                "name": "Type",
                "type": "select",
                "selections": [
                    "Head and Shoulder",
                    "Inverse Head and Shoulder"
                ]
            }
        ]
    },
    {
        "name": "Triangle",
        "parametres": [
            {
                "name": "Window",
                "type": "int",
                "default": 5
            },
            {
                "name": "Type",
                "type": "select",
                "selections": [
                    "Ascending Triangle",
                    "Descending Triangle"
                ]
            }
        ]
    },
    {
        "name": "Wedge",
        "parametres": [
            {
                "name": "Window",
                "type": "int",
                "default": 5
            },
            {
                "name": "Type",
                "type": "select",
                "selections": [
                    "Wedge Up",
                    "Wedge Down"
                ]
            }
        ]
    },
    ## NEW
    {
        "name": "Multiple Tops/Bottoms",
        "parametres": [
            {
                "name": "Window",
                "type": "int",
                "default": 15
            },
            {
                "name": "Type",
                "type": "select",
                "selections": [
                    "Multiple Top",
                    "Multiple Bottom"
                ]
            }
        ]
    },
    {
        "name": "Channel",
        "parametres": [
            {
                "name": "Window",
                "type": "int",
                "default": 15
            },
            {
                "name": "Type",
                "type": "select",
                "selections": [
                    "Channel Up",
                    "Channel Down"
                ]
            }
        ]
    },
    {
        "name": "Double Top/Bottom",
        "parametres": [
            {
                "name": "Window",
                "type": "int",
                "default": 15
            },
            {
                "name": "Type",
                "type": "select",
                "selections": [
                    "Double Top",
                    "Double Bottom"
                ]
            }
        ]
    }
]