import React, { useEffect, useState, useRef } from "react";
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  Dimensions,
  Image,
} from "react-native";
import Header from "../components/Header";

export default function Home({ navigation }) {
  const { height: windowHeight } = Dimensions.get("window");
  const topOffset = Math.round(windowHeight * 0.08);

  // HARDED CODED IP USED FOR TESTING PURPOSES JUST FOR NOW I WILL REMOVE IT LATER TRUST
  const STREAM_URL = "http://172.23.181.202:8080/frame";

  const [ts, setTs] = useState(Date.now());
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => {
      setTs(Date.now());
    }, 200);
    return () => clearInterval(intervalRef.current);
  }, []);

  const uri = `${STREAM_URL}?t=${ts}`;

  return (
    <View style={[styles.container, { paddingTop: topOffset }]}>
      <Header navigation={navigation} currentScreen="Home" />

      <Text style={styles.screenTitle}>Live View</Text>

      <View style={styles.videoContainer}>
        <View style={styles.videoPlaceholder}>
          <Image
            source={{ uri }}
            style={styles.streamImage}
            resizeMode="cover"
            onLoad={() => setLoading(false)}
            onError={() => setLoading(true)}
          />

          {loading && (
            <View style={styles.overlayCenter} pointerEvents="none">
              <ActivityIndicator size="large" color="#666" />
              <Text style={styles.connectingText}>Connecting to device...</Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  screenTitle: {
    color: "#fff",
    fontSize: 30,
    textAlign: "center",
    marginTop: 18,
    marginBottom: 18,
    fontWeight: "600",
  },
  videoContainer: { alignItems: "center", paddingHorizontal: 16 },
  videoPlaceholder: {
    width: "95%",
    aspectRatio: 1,
    backgroundColor: "#000",
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 12,
    borderWidth: 3,
    borderColor: "#fff",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.12,
    shadowRadius: 10,
    elevation: 6,
  },
  streamImage: { width: "100%", height: "100%", borderRadius: 12 },
  overlayCenter: {
    position: "absolute",
    alignItems: "center",
    justifyContent: "center",
  },
  connectingText: { color: "#fff", marginTop: 12, fontSize: 18 },
});
