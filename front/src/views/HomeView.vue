<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card class="pa-6" max-width="600" elevation="4">
      <v-card-title class="text-h5 font-weight-bold">API 선택</v-card-title>
      <v-card
        class="mb-2"
        color="blue-grey-lighten-5"
        variant="outlined"
        @click="goUpload"
        style="cursor: pointer"
      >
        <v-card-title class="text-subtitle-1 font-weight-bold">📄 PDF → Markdown 변환</v-card-title>
        <v-card-text class="text-body-2">
          PDF 강의자료를 정돈된 마크다운 문서로 변환해주는 기능입니다.
        </v-card-text>
      </v-card>
    </v-card>
  </v-container>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    goUpload() {
      this.$router.push('/upload')
    }
  }
}
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px); /* 앱바 높이만큼 고려 */
}
</style>
