const app = {}

let init = (app) => {
  app.data = {
    //
    bcm_home_url: "/bcm/index",
    bcm_devices_url: "/bcm/devices",
    bcm_results_url: "/bcm/results",
    devices: [],
    device: null,
    devices_by_role: null,
    device_roles: null,
    device_role: null,
    select_device: null,
    select_role: null,
  }
  
  app.bcm_get_devices = function() {
    // Get devices in response to page load
    const url = "/bcm/get_devices"
    axios.get(url).then(function(response) {
      app.vue.devices = response.data.devices
    })
  }

  app.bcm_get_device_roles = function() {
    // Get device_roles in response to page load
    const url = "/bcm/get_device_roles"
    axios.get(url).then(function(response) {
      app.vue.device_roles = response.data.roles
    })
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

  app.bcm_select_device_role = function(event) {
    const role = event.target.value
    const url = "/bcm/get_devices_by_role/" + role
    axios.get(url).then(function(response) {
      app.vue.devices_by_role = response.data.devices_by_role
    })
    //app.vue.devices_by_role = app.vue.devices.find(( device ) => device.device_roles.includes(role))
    //console.log(role)
    //console.log(app.vue.devices_by_role[0])
    app.vue.select_device = null
    //const result = inventory.find(({ name }) => name === "cherries");
    //app.vue.devices_by_role = app.vue.devices.find(({ dev }) => dev.device_roles.includes(role))
    //app.vue.devices_by_role = app.vue.devices.find(({ device_roles }) => device_roles.includes(role))
    //console.log(app.vue.devices_by_role)
  }

  app.bcm_selected_device = function(event) {
    const device_id = event.target.value
    app.vue.device = app.vue.devices_by_role.find(({ id }) => id === device_id)
    console.log("Test - Selected Device ", this.select_device)
  }

  app.methods = {
    button_run_cmds: app.bcm_button_run_cmds,
    button_run_cmds_role: app.bcm_button_run_cmds_role,
    select_device_role: app.bcm_select_device_role,
    selected_device: app.bcm_selected_device,
  }

  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  })

  app.init = () => {
    //load the devices...
    app.bcm_get_devices()
    app.bcm_get_device_roles()
  }
  
  app.init()
}

init(app)
