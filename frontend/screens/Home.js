import React, { useState, useEffect } from "react";
import { View, Text, StyleSheet, Dimensions, ActivityIndicator } from "react-native";
import { VideoView, useVideoPlayer } from "expo-video";
import Header from "../components/Header";

export default function Home({ navigation }) {
  const { height: windowHeight } = Dimensions.get("window");
  const topOffset = Math.round(windowHeight * 0.08);

  // Replace with your active IVS Playback URL
  const STREAM_URL =
    "https://462fa9198398.us-west-2.playback.live-video.net/api/video/v1/us-west-2.183631317991.channel.QEJWemYiWcPj.m3u8";

  const [loading, setLoading] = useState(true);

  // Initialize video player
  const player = useVideoPlayer(STREAM_URL, (player) => {
    player.play();
  });

  // Fallback: hide loader after 5 seconds if player exists
  useEffect(() => {
    if (player && loading) {
      const timeout = setTimeout(() => {
        setLoading(false);
      }, 5000);
      return () => clearTimeout(timeout);
    }
  }, [player, loading]);

  // Handle playback readiness + errors
  useEffect(() => {
    const hideLoader = () => setLoading(false);
    const showLoader = () => setLoading(true);

    if (player) {
      player.addListener("firstVideoFrameRendered", hideLoader);
      player.addListener("playing", hideLoader);
      player.addListener("error", showLoader);
    }

    return () => {
      if (player) {
        player.removeListener("firstVideoFrameRendered", hideLoader);
        player.removeListener("playing", hideLoader);
        player.removeListener("error", showLoader);
      }
    };
  }, [player]);

  return (
    <View style={[styles.container, { paddingTop: topOffset }]}>
      <Header navigation={navigation} currentScreen="Home" />

      <Text style={styles.screenTitle}>Live View</Text>

      <View style={styles.videoWrapper}>
        {/* VIDEO PLAYER DISPLAY */}
        <VideoView
          player={player}
          style={styles.video}
          contentFit="cover"
          fullscreenOptions={{ enabled: true }}
        />

        {/* LOADING OVERLAY */}
        {loading && (
          <View pointerEvents="none" style={styles.overlayCenter}>
            <ActivityIndicator size="large" color="#fff" />
            <Text style={styles.connectingText}>Connecting to Live Stream...</Text>
          </View>
        )}
      </View>

      {/* Activity Log */}
      <View style={styles.logBox}>
        <Text style={styles.logTitle}>Activity Log</Text>
        <Text style={styles.logText}>{loading ? "Connecting..." : "Stream Live!"}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },

  screenTitle: {
    color: "#fff",
    fontSize: 28,
    textAlign: "center",
    marginVertical: 18,
    fontWeight: "600",
  },

  videoWrapper: {
    width: "95%",
    aspectRatio: 1,
    backgroundColor: "#000",
    borderRadius: 12,
    borderWidth: 2,
    borderColor: "#fff",
    alignSelf: "center",
    overflow: "hidden",
  },

  video: {
    width: "100%",
    height: "100%",
  },

  overlayCenter: {
    position: "absolute",
    top: 0,
    left: 0,
    width: "100%",
    height: "100%",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "rgba(0,0,0,0.45)",
    zIndex: 999,
  },

  connectingText: { color: "#fff", marginTop: 10, fontSize: 16 },

  logBox: {
    width: "90%",
    backgroundColor: "#111",
    borderRadius: 10,
    marginTop: 18,
    alignSelf: "center",
    padding: 12,
    borderWidth: 2,
    borderColor: "#fff",
  },

  logTitle: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
  },

  logText: {
    color: "#bbb",
    fontSize: 15,
    marginTop: 4,
    fontStyle: "italic",
  },
});
