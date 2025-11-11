import React from "react";
import { View, Text, Button, StyleSheet, ActivityIndicator } from "react-native";

export default function Home({ navigation }) {
  return (
    <View style={styles.container}>
      <View style={styles.videoContainer}>
        <View style={styles.videoPlaceholder}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.connectingText}>Connecting to device...</Text>
        </View>
      </View>

      <View style={styles.controls}>
        <View style={styles.settingsButtonWrap}>
          <Button title="Settings" onPress={() => navigation.navigate("Settings")} />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#fff" },
  videoContainer: { flex: 1, alignItems: "center", justifyContent: "center" },
  videoPlaceholder: {
    width: "95%",
    aspectRatio: 16 / 9,
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
  },
  connectingText: { color: "#fff", marginTop: 12 },
  controls: { paddingHorizontal: 16 },
  settingsButtonWrap: {
    position: "absolute",
    bottom: 110,
    left: 0,
    right: 0,
    alignItems: "center",
  },
});
