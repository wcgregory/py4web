let app = {}

let init = (app) => {
  app.data = {}
  app.bcm_run_commands_button = function(device_id) {
    console.log("Test - Button Pressed")
    let url="/bcm/run_commands/" + device_id
    axios.get(url).then(function(response) {
      console.log(response.data)
    })
  }
  app.methods = {bcm_run_commands_button: app.bcm_run_commands_button}
  app.vue = new Vue({
    el: "#vue-target",
    data: app.data,
    methods: app.methods
  })
  app.init = () => {}
  app.init()
}

init(app)
