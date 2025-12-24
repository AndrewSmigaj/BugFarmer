using UnityEngine;

namespace BugFarmer.Player
{
    /// <summary>
    /// Smooth camera follow for 2D top-down view.
    /// Attach to Main Camera.
    /// </summary>
    public class CameraFollow : MonoBehaviour
    {
        [SerializeField] private Transform target;
        [SerializeField] private float smoothTime = 0.15f; // Time to reach target
        [SerializeField] private float zOffset = -10f;

        private Vector3 _velocity;

        private void LateUpdate()
        {
            if (target == null)
                return;

            Vector3 targetPos = new Vector3(target.position.x, target.position.y, zOffset);
            transform.position = Vector3.SmoothDamp(transform.position, targetPos, ref _velocity, smoothTime);
        }

        /// <summary>
        /// Set the follow target at runtime.
        /// </summary>
        public void SetTarget(Transform newTarget)
        {
            target = newTarget;
        }

        /// <summary>
        /// Instantly snap camera to target position.
        /// </summary>
        public void SnapToTarget()
        {
            if (target != null)
            {
                transform.position = new Vector3(target.position.x, target.position.y, zOffset);
                _velocity = Vector3.zero;
            }
        }
    }
}
