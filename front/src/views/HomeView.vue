<template>
  <v-container>
    <v-card>
      <v-card-title>홈</v-card-title>
      <VBanner>API 종류를 선택하세요</VBanner>
      <v-card-actions>
        <v-btn color="primary" variant="tonal" @click="goUpload">PDF를 마크다운으로 변환하기
        </v-btn>
      </v-card-actions>
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
