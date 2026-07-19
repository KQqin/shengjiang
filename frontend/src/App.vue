<script setup>
import { onLaunch } from '@dcloudio/uni-app'

onLaunch(() => {})
</script>

<style lang="scss">
@import './styles/fonts.scss';

html.teaching-fullscreen,
html:fullscreen,
html:-webkit-full-screen {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

html.teaching-fullscreen body,
html:fullscreen body,
html:-webkit-full-screen body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  margin: 0;
}

#app,
uni-app,
uni-page,
uni-page-wrapper,
uni-page-body {
  min-height: 100%;
}

html.teaching-fullscreen #app,
html:fullscreen #app,
html:-webkit-full-screen #app {
  height: 100%;
  min-height: 100%;
}
</style>
