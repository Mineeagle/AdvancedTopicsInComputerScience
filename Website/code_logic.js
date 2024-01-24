const json_dummy_data_url = """[
    {
        "location": {
            "latitude": 37.419734,
            "longitude": -122.0827784
        },
        "level": 0.9
    },
    {
        "location": {
            "latitude": 37.4197318,
            "longitude": -122.0826233
        },
        "level": 1.3
    },
    {
        "location": {
            "latitude": 37.419734,
            "longitude": -122.08077919999998
        },
        "level": -0.3
    },
    {
        "location": {
            "latitude": 37.41954,
            "longitude": -122.08262750000002
        },
        "level": 0.456
    }
]"""

function get_json_data() {
    res = null
    let text = localStorage.getItem(json_dummy_data_url)
    res = JSON.parse(text)

    console.log(res)
    return res
}

res = null;
let text = localStorage.getItem(json_dummy_data_url);
res = JSON.parse(text);

console.log(res);