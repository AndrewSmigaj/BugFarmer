// BugFarmer animated water: a copy of BugFarmer/SpriteLitWorld (URP 2D lit sprite) with water added to the
// LIT (Universal2D) fragment only. All animation is driven off WORLD position (a worldUV varying) so it is
// seamless across tile boundaries (Cyanilux 2D-water rule); any UV refraction is edge-faded so it never
// samples a neighbour tile, and the caustic highlight is MULTIPLICATIVE so it fades with the scene at night.
// It stays 2D-lit (dims at night + under the darkness overlay). Style props are dials: calm (default),
// flowing (scroll dir/speed), sparkle (sparkle strength). Water props are in ALL 3 CBUFFERs so the SRP
// batcher sees one UnityPerMaterial layout, even though only the lit pass uses them.
Shader "BugFarmer/WaterAnimated"
{
    Properties
    {
        _MainTex("Diffuse", 2D) = "white" {}
        _WindStrength("Wind Strength", Float) = 0
        _WindSpeed("Wind Speed", Float) = 1.5
        _BobStrength("Bob Strength", Float) = 0
        _BobSpeed("Bob Speed", Float) = 1
        _FlashColor("Flash Color", Color) = (1,1,1,1)
        _FlashAmount("Flash Amount", Range(0,1)) = 0
        // Water dials
        _WaterAmp("Water Distortion", Float) = 0.05
        _WaterFreq("Water Frequency", Float) = 4.19
        _ScrollSpeed("Water Speed", Float) = 0.66
        _ScrollDirX("Scroll Dir X", Float) = 0.24
        _ScrollDirY("Scroll Dir Y", Float) = 0.45
        _Shimmer("Shimmer", Float) = 0
        _SparkleStrength("Sparkle", Float) = 0
        _MaskTex("Mask", 2D) = "white" {}
        _NormalMap("Normal Map", 2D) = "bump" {}
        [MaterialToggle] _ZWrite("ZWrite", Float) = 0

        // Legacy properties. They're here so that materials using this shader can gracefully fallback to the legacy sprite shader.
        [HideInInspector] _Color("Tint", Color) = (1,1,1,1)
        [HideInInspector] _RendererColor("RendererColor", Color) = (1,1,1,1)
        [HideInInspector] _AlphaTex("External Alpha", 2D) = "white" {}
        [HideInInspector] _EnableExternalAlpha("Enable External Alpha", Float) = 0
    }

    SubShader
    {
        Tags {"Queue" = "Transparent" "RenderType" = "Transparent" "RenderPipeline" = "UniversalPipeline" }

        Blend SrcAlpha OneMinusSrcAlpha, One OneMinusSrcAlpha
        Cull Off
        ZWrite [_ZWrite]

        Pass
        {
            Tags { "LightMode" = "Universal2D" }

            HLSLPROGRAM
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/2D/Include/Core2D.hlsl"

            #pragma vertex CombinedShapeLightVertex
            #pragma fragment CombinedShapeLightFragment

            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/Shaders/2D/Include/ShapeLightShared.hlsl"

            // GPU Instancing
            #pragma multi_compile_instancing
            #pragma multi_compile _ DEBUG_DISPLAY SKINNED_SPRITE

            struct Attributes
            {
                float3 positionOS   : POSITION;
                float4 color        : COLOR;
                float2 uv           : TEXCOORD0;
                float3 normal       : NORMAL;
                UNITY_SKINNED_VERTEX_INPUTS
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4  positionCS  : SV_POSITION;
                half4   color       : COLOR;
                float2  uv          : TEXCOORD0;
                half2   lightingUV  : TEXCOORD1;
                float2  worldUV     : TEXCOORD4;   // world position for seamless water animation
                #if defined(DEBUG_DISPLAY)
                float3  positionWS  : TEXCOORD2;
                half3  normalWS     : TEXCOORD3;
                #endif
                UNITY_VERTEX_OUTPUT_STEREO
            };

            #include "Packages/com.unity.render-pipelines.universal/Shaders/2D/Include/LightingUtility.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/DebugMipmapStreamingMacros.hlsl"

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);
            UNITY_TEXTURE_STREAMING_DEBUG_VARS_FOR_TEX(_MainTex);

            TEXTURE2D(_MaskTex);
            SAMPLER(sampler_MaskTex);

            TEXTURE2D(_NormalMap);
            SAMPLER(sampler_NormalMap);

            // NOTE: Do not ifdef the properties here as SRP batcher can not handle different layouts.
            CBUFFER_START(UnityPerMaterial)
                half4 _Color;
                half4 _FlashColor;
                float _WindStrength;
                float _WindSpeed;
                float _BobStrength;
                float _BobSpeed;
                float _FlashAmount;
                float _WaterAmp;
                float _WaterFreq;
                float _ScrollSpeed;
                float _ScrollDirX;
                float _ScrollDirY;
                float _Shimmer;
                float _SparkleStrength;
            CBUFFER_END

            #if USE_SHAPE_LIGHT_TYPE_0
            SHAPE_LIGHT(0)
            #endif

            #if USE_SHAPE_LIGHT_TYPE_1
            SHAPE_LIGHT(1)
            #endif

            #if USE_SHAPE_LIGHT_TYPE_2
            SHAPE_LIGHT(2)
            #endif

            #if USE_SHAPE_LIGHT_TYPE_3
            SHAPE_LIGHT(3)
            #endif

            Varyings CombinedShapeLightVertex(Attributes v)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(v);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                UNITY_SKINNED_VERTEX_COMPUTE(v);

                SetUpSpriteInstanceProperties();
                v.positionOS = UnityFlipSprite(v.positionOS, unity_SpriteProps.xy);
                float3 originWS = TransformObjectToWorld(float3(0.0, 0.0, 0.0));
                float3 posWS = TransformObjectToWorld(v.positionOS);
                posWS.x += sin(originWS.x * 0.6 + _Time.y * _WindSpeed) * _WindStrength * v.uv.y;
                posWS.y += sin((originWS.x + originWS.y) * 0.5 + _Time.y * _BobSpeed) * _BobStrength;
                o.worldUV = posWS.xy;   // seamless: animation keyed on world position, continuous across tiles
                o.positionCS = TransformWorldToHClip(posWS);
                #if defined(DEBUG_DISPLAY)
                o.positionWS = TransformObjectToWorld(v.positionOS);
                o.normalWS = TransformObjectToWorldDir(v.normal);
                #endif
                o.uv = v.uv;
                o.lightingUV = half2(ComputeScreenPos(o.positionCS / o.positionCS.w).xy);

                o.color = v.color * _Color * unity_SpriteColor;
                return o;
            }

            #include "Packages/com.unity.render-pipelines.universal/Shaders/2D/Include/CombinedShapeLightShared.hlsl"

            half4 CombinedShapeLightFragment(Varyings i) : SV_Target
            {
                // --- animated water (world-space so it is seamless across tiles) ---
                float2 wuv = i.worldUV;
                float t = _Time.y * _ScrollSpeed;
                float2 p = wuv + float2(_ScrollDirX, _ScrollDirY) * t;   // directional drift (0 = calm pond)

                // Refraction: a small, smooth world-space UV warp, edge-faded so it never samples a neighbour
                // tile. (No posterize — snapping the sample UV to texels flickers under bilinear filtering as
                // it animates/pans, which read as "static".)
                float2 e = min(i.uv, 1.0 - i.uv);
                float edgeFade = saturate(min(e.x, e.y) * 6.0);
                float2 warp = float2(sin(p.y * _WaterFreq + t), sin(p.x * _WaterFreq * 1.3 - t))
                            + 0.5 * float2(sin(p.y * _WaterFreq * 2.1 - t * 1.4), sin(p.x * _WaterFreq * 1.9 + t * 1.2));
                float2 duv = i.uv + warp * (_WaterAmp * edgeFade);

                const half4 main = i.color * SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, duv);
                const half4 mask = SAMPLE_TEXTURE2D(_MaskTex, sampler_MaskTex, i.uv);
                const half3 normalTS = UnpackNormal(SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, i.uv));

                SurfaceData2D surfaceData;
                InputData2D inputData;

                InitializeSurfaceData(main.rgb, main.a, mask, normalTS, surfaceData);
                InitializeInputData(i.uv, i.lightingUV, inputData);

#if defined(DEBUG_DISPLAY)
                SETUP_DEBUG_TEXTURE_DATA_2D_NO_TS(inputData, i.positionWS, i.positionCS, _MainTex);
                surfaceData.normalWS = i.normalWS;
#endif

                half4 litColor = CombinedShapeLightShared(surfaceData, inputData);

                // Caustic highlight: a gentle world-space brightness ripple applied MULTIPLICATIVELY, so it
                // scales with the lit surface and fades naturally as it gets dark (an ADDITIVE version showed a
                // fixed interference pattern that dominated at dusk). ~1 +/- _Shimmer around the lit colour.
                float caustic = 0.5 * sin(p.x * _WaterFreq + t) + 0.5 * sin(p.y * _WaterFreq * 0.9 - t * 0.7); // -1..1
                litColor.rgb += litColor.rgb * (_Shimmer * caustic);

                // Occasional sparkle glints: threshold a hashed world cell that ticks over time.
                float2 cell = floor(wuv * 6.0 + floor(t));
                float h = frac(sin(dot(cell, float2(12.9898, 78.233))) * 43758.5453);
                litColor.rgb += _SparkleStrength * step(0.985, h) * main.a;

                litColor.rgb = lerp(litColor.rgb, _FlashColor.rgb, _FlashAmount);   // inherited (unused for water)
                return litColor;
            }
            ENDHLSL
        }

        Pass
        {
            Tags { "LightMode" = "NormalsRendering"}

            HLSLPROGRAM
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/2D/Include/Core2D.hlsl"

            #pragma vertex NormalsRenderingVertex
            #pragma fragment NormalsRenderingFragment

            // GPU Instancing
            #pragma multi_compile_instancing
            #pragma multi_compile _ SKINNED_SPRITE

            struct Attributes
            {
                float3 positionOS   : POSITION;
                float4 color        : COLOR;
                float2 uv           : TEXCOORD0;
                float3 normal       : NORMAL;
                float4 tangent      : TANGENT;
                UNITY_SKINNED_VERTEX_INPUTS
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4  positionCS      : SV_POSITION;
                half4   color           : COLOR;
                float2  uv              : TEXCOORD0;
                half3   normalWS        : TEXCOORD1;
                half3   tangentWS       : TEXCOORD2;
                half3   bitangentWS     : TEXCOORD3;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);

            TEXTURE2D(_NormalMap);
            SAMPLER(sampler_NormalMap);

            // NOTE: Do not ifdef the properties here as SRP batcher can not handle different layouts.
            CBUFFER_START( UnityPerMaterial )
                half4 _Color;
                half4 _FlashColor;
                float _WindStrength;
                float _WindSpeed;
                float _BobStrength;
                float _BobSpeed;
                float _FlashAmount;
                float _WaterAmp;
                float _WaterFreq;
                float _ScrollSpeed;
                float _ScrollDirX;
                float _ScrollDirY;
                float _Shimmer;
                float _SparkleStrength;
            CBUFFER_END

            Varyings NormalsRenderingVertex(Attributes attributes)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(attributes);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                UNITY_SKINNED_VERTEX_COMPUTE(attributes);

                SetUpSpriteInstanceProperties();
                attributes.positionOS = UnityFlipSprite(attributes.positionOS, unity_SpriteProps.xy);
                float3 originWS = TransformObjectToWorld(float3(0.0, 0.0, 0.0));
                float3 posWS = TransformObjectToWorld(attributes.positionOS);
                posWS.x += sin(originWS.x * 0.6 + _Time.y * _WindSpeed) * _WindStrength * attributes.uv.y;
                posWS.y += sin((originWS.x + originWS.y) * 0.5 + _Time.y * _BobSpeed) * _BobStrength;
                o.positionCS = TransformWorldToHClip(posWS);
                o.uv = attributes.uv;
                o.color = attributes.color * _Color * unity_SpriteColor;
                o.normalWS = TransformObjectToWorldDir(attributes.normal);
                o.tangentWS = TransformObjectToWorldDir(attributes.tangent.xyz);
                o.bitangentWS = cross(o.normalWS, o.tangentWS) * attributes.tangent.w;
                return o;
            }

            #include "Packages/com.unity.render-pipelines.universal/Shaders/2D/Include/NormalsRenderingShared.hlsl"

            half4 NormalsRenderingFragment(Varyings i) : SV_Target
            {
                const half4 mainTex = i.color * SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, i.uv);
                const half3 normalTS = UnpackNormal(SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, i.uv));

                return NormalsRenderingShared(mainTex, normalTS, i.tangentWS.xyz, i.bitangentWS.xyz, i.normalWS.xyz);
            }
            ENDHLSL
        }

        Pass
        {
            Tags { "LightMode" = "UniversalForward" "Queue"="Transparent" "RenderType"="Transparent"}

            HLSLPROGRAM
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/Shaders/2D/Include/Core2D.hlsl"
            #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/DebugMipmapStreamingMacros.hlsl"
            #if defined(DEBUG_DISPLAY)
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Debug/Debugging2D.hlsl"
            #endif

            #pragma vertex UnlitVertex
            #pragma fragment UnlitFragment

            // GPU Instancing
            #pragma multi_compile_instancing
            #pragma multi_compile _ DEBUG_DISPLAY SKINNED_SPRITE

            struct Attributes
            {
                float3 positionOS   : POSITION;
                float4 color        : COLOR;
                float2 uv           : TEXCOORD0;
                UNITY_SKINNED_VERTEX_INPUTS
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4  positionCS      : SV_POSITION;
                float4  color           : COLOR;
                float2  uv              : TEXCOORD0;
                #if defined(DEBUG_DISPLAY)
                float3  positionWS  : TEXCOORD2;
                #endif
                UNITY_VERTEX_OUTPUT_STEREO
            };

            TEXTURE2D(_MainTex);
            SAMPLER(sampler_MainTex);
            UNITY_TEXTURE_STREAMING_DEBUG_VARS_FOR_TEX(_MainTex);

            // NOTE: Do not ifdef the properties here as SRP batcher can not handle different layouts.
            CBUFFER_START( UnityPerMaterial )
                half4 _Color;
                half4 _FlashColor;
                float _WindStrength;
                float _WindSpeed;
                float _BobStrength;
                float _BobSpeed;
                float _FlashAmount;
                float _WaterAmp;
                float _WaterFreq;
                float _ScrollSpeed;
                float _ScrollDirX;
                float _ScrollDirY;
                float _Shimmer;
                float _SparkleStrength;
            CBUFFER_END

            Varyings UnlitVertex(Attributes attributes)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(attributes);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                UNITY_SKINNED_VERTEX_COMPUTE(attributes);

                SetUpSpriteInstanceProperties();
                attributes.positionOS = UnityFlipSprite( attributes.positionOS, unity_SpriteProps.xy);
                float3 originWS = TransformObjectToWorld(float3(0.0, 0.0, 0.0));
                float3 posWS = TransformObjectToWorld(attributes.positionOS);
                posWS.x += sin(originWS.x * 0.6 + _Time.y * _WindSpeed) * _WindStrength * attributes.uv.y;
                posWS.y += sin((originWS.x + originWS.y) * 0.5 + _Time.y * _BobSpeed) * _BobStrength;
                o.positionCS = TransformWorldToHClip(posWS);
                #if defined(DEBUG_DISPLAY)
                o.positionWS = TransformObjectToWorld(attributes.positionOS);
                #endif
                o.uv = attributes.uv;
                o.color = attributes.color * _Color * unity_SpriteColor;
                return o;
            }

            float4 UnlitFragment(Varyings i) : SV_Target
            {
                float4 mainTex = i.color * SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, i.uv);

                #if defined(DEBUG_DISPLAY)
                SurfaceData2D surfaceData;
                InputData2D inputData;
                half4 debugColor = 0;

                InitializeSurfaceData(mainTex.rgb, mainTex.a, surfaceData);
                InitializeInputData(i.uv, inputData);
                SETUP_DEBUG_TEXTURE_DATA_2D_NO_TS(inputData, i.positionWS, i.positionCS, _MainTex);

                if(CanDebugOverrideOutputColor(surfaceData, inputData, debugColor))
                {
                    return debugColor;
                }
                #endif

                return mainTex;
            }
            ENDHLSL
        }
    }
}
