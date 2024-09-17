let app = {}

let init = (app) => {
  app.data = {
    //
    devices: []
  }
  
  app.bcm_button_run_cmds = function(device_id) {
    console.log("Test - Button Pressed")
    let url="/bcm/run_commands/" + device_id
    axios.get(url).then(function(response) {
      console.log(response.data)
    })
  }

  app.bcm_button_run_cmds_role = function(device_role) {
    console.log("Test - Button Pressed")
    let url="/bcm/run_commands_by_role/" + device_role
    axios.get(url).then(function(response) {
      console.log(response.data)
    })
  }

  app.get_devices = function() {
    // Gets devices in response to page load
    const url = "/bcm/get_devices"
    axios.get(url).then(function(response) {
      app.vue.devices = response.data.devices
  })
  }

  app.select_device = function() {
    console.log("Test - Selected Device")
  }

  app.methods = {
    bcm_button_run_cmds: app.bcm_button_run_cmds,
    bcm_button_run_cmds_role: app.bcm_button_run_cmds_role
  }

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  })

  app.init = () => {
    //load the devices...
    app.get_devices()
  }
  
  app.init()
}

init(app)
